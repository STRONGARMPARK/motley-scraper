import os
from datetime import datetime
import argparse
import logging
from foolcalls.config import Aws, FoolCalls
import json
import boto3
from foolcalls import helpers, extractors
from io import BytesIO
import gzip
import shutil
from lxml import html
import multiprocessing as mp
import requests
import random

log = logging.getLogger(__name__)

aws_session = boto3.Session(aws_access_key_id=Aws.AWS_KEY,
                            aws_secret_access_key=Aws.AWS_SECRET)


# ---------------------------------------------------------------------------
# SCRAPE LINKS OF OF A GIVEN PAGE
# ---------------------------------------------------------------------------
def request_html_w_urls(page_num, url):
    request = dict(url=url,
                   params={'page': page_num},
                   headers={'User-Agent': random.choice(FoolCalls.USER_AGENT_LIST)})

    log.info(f'request: {request}')

    response = requests.get(**request)
    assert response.status_code == 200
    return response


def scrape_transcript_urls(html_text, page_num=1):
    html_selector = html.fromstring(html_text)
    call_urls = extractors.get_call_urls(html_selector, page_num)
    return call_urls


def scrape_transcript_urls_by_page(page_num):
    response = request_html_w_urls(page_num, FoolCalls.INVESTING_NEWS_LINKS_ROOT)
    call_urls_ext = scrape_transcript_urls(response.text)
    call_urls = [f'{FoolCalls.ROOT}{call_url_ext}' for call_url_ext in call_urls_ext]
    return call_urls

def scrape_author_article_urls_by_page(page_num, author_num):
    try:
        response = request_html_w_urls(page_num, FoolCalls.AUTHOR_ARTICLE_LINKS_ROOT + "/" + str(author_num) + "/")
        call_urls_ext = scrape_transcript_urls(response.text, page_num)
        call_urls = [f'{FoolCalls.ROOT}{call_url_ext}' for call_url_ext in call_urls_ext]
        return call_urls
    except Exception as e:
        print("Error: ", e)
        return []


# ---------------------------------------------------------------------------
# SCRAPE TRANSCRIPT
# ---------------------------------------------------------------------------
def scrape_transcript(html_text: bytes) -> dict:


    # top level html elements (aka containers)
    # returns a dictionary wherein each key is a different container object
    # no information is being extracted yet; different parts of the page are being isolated here
    elements = extractors.extract_elements(html_text)

    return elements


def get_raw_transcript(outputpath, key):
    if outputpath == 's3':
        html_content = get_raw_transcript_from_s3(key)
    else:
        html_content = get_raw_transcript_from_local(outputpath, key)

    return html_content


def get_raw_transcript_from_s3(file_path):
    input_file_buffer = BytesIO()
    output_file_buffer = BytesIO()

    s3_client = aws_session.client('s3', region_name=Aws.S3_REGION_NAME)
    s3_client.download_fileobj(Bucket=Aws.S3_FOOLCALLS_BUCKET,
                               Key=file_path,
                               Fileobj=input_file_buffer)

    input_file_buffer.seek(0)
    with gzip.GzipFile(fileobj=input_file_buffer, mode='rb') as gz:
        shutil.copyfileobj(gz, output_file_buffer)

    return output_file_buffer.getvalue()


def get_raw_transcript_from_local(outputpath, file_path):
    output_file_buffer = BytesIO()
    with gzip.open(f'{outputpath.rstrip("/")}/{file_path}', 'rb') as f_in:
        shutil.copyfileobj(f_in, output_file_buffer)

    return output_file_buffer.getvalue()


def save_transcript(outputpath: str, key: str, output: dict) -> None:
    if outputpath == 's3':
        put_transcript_in_s3(key, output)
    else:
        save_transcript_local(outputpath, key, output)


def save_transcript_local(outputpath: str, key: str, output: dict) -> None:
    output_path = f'{outputpath.rstrip("/")}/{key}'
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    with open(output_path, 'w') as f:
        json.dump(output, f)
    print(f'wrote: {key} locally to {outputpath}')


def put_transcript_in_s3(key: str, output: dict) -> None:
    s3_client = aws_session.client('s3', region_name=Aws.S3_REGION_NAME)
    s3_client.put_object(Bucket=Aws.S3_FOOLCALLS_BUCKET,
                         Key=key,
                         Body=json.dumps(output))

    s3_output_url = f'{Aws.S3_OBJECT_ROOT}/{Aws.S3_FOOLCALLS_BUCKET}/{key}'
    log.info(f'pid[{mp.current_process().pid}] s3 upload success: {s3_output_url}')
    print(f'pid[{mp.current_process().pid}] s3 upload success: {s3_output_url}')


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main(cid, outputpath, key):
    try:
        html_content = get_raw_transcript(outputpath, key)
        process_transcript(cid, html_content, outputpath)
    except Exception as e:
        log.error(f'error: {e}')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
# everything below will only be executed if this script is called from the command line
# if this file is imported, nothing below will be executed
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='scrape the contents of a call from a raw html file')
    parser.add_argument('cid', help='call id to scrape')
    parser.add_argument('outputpath', help=f'parent dir that stores all outputs (like a local s3 bucket); if '
                                           f'outputpath==\'s3\', output is uploaded to the Aws.OUPUT_BUCKET '
                                           f'parameter defined in config.py')
    parser.add_argument('key', help='local key or s3 key of incoming html file; '
                                    'do not include outputpath or s3 bucket in key')
    args = parser.parse_args()

    # logging (will inherit log calls from utils.pricing and utils.s3_helpers)
    this_file = os.path.basename(__file__).replace('.py', '')
    log_id = f'{this_file}_{datetime.now().strftime("%Y%m%dT%H%M%S")}'
    logging.basicConfig(filename=f'./logs/{log_id}.log', level=logging.INFO,
                        format=f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # run main
    main(args.cid, args.key, args.outputpath)
    log.info(f'successfully completed script')
