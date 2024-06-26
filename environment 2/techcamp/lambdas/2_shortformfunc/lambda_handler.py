# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Video Shortform: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import json
import os
import uuid
import time
import re
import base64


MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
BEDROCK_REGION_NAME=os.environ.get('BEDROCK_REGION_NAME', 'us-west-2')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MEDIA_CONVERT_ROLE = os.environ.get('MEDIA_CONVERT_ROLE')

bedrock_runtime = boto3.client(
  service_name='bedrock-runtime',
  region_name=BEDROCK_REGION_NAME
)

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
mediaconvert = boto3.client('mediaconvert')


def get_response(user_prompt, system_prompt):
    body = {
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096
    }

    # Run Bedrock API
    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(body)
    )

    response_body = json.loads(response.get('body').read())
    output = response_body['content'][0]['text']

    return output


def stitching_clips(video_name, tracks):
    # HH:MM:SS:FF or HH:MM:SS;FF
    # where HH is the hour, MM is the minute, SS is the second, and FF is the frame number.
    # FF, if 24 frame rate, FF is from 0 to 23
    tracks = sorted(tracks)
    start_time, end_time = tracks.pop(0)
    temp = [start_time.split('.')[0] + ':00', end_time.split('.')[0] + ':00']

    for start_time, end_time in tracks:
        st = start_time.split('.')[0] + ':00'
        et = end_time.split('.')[0] + ':00'
        if temp[-1] == st:
            temp.pop()
        else:
            temp.append(st)
        
        temp.append(et)
        
    print(temp)
    
    if len(temp) % 2 != 0:
        print('temp is odd')
        temp.pop()
    
    input_clippings = []
    for st, et in zip(temp[0::2], temp[1::2]):
        print(st, et)
        input_clippings.append(
            {
                "StartTimecode": st,
                "EndTimecode": et
            }            
        )

    video_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('UTF-8').rstrip('=')
    shortened_video_name = f'{video_id}_{video_name}'
    only_name, _ = os.path.splitext(shortened_video_name)
    settings = {
        "TimecodeConfig": {
            "Source": "ZEROBASED"
        },
        "OutputGroups": [
            {
                # "CustomName": "test",
                # "Name": "File Group",
                "Outputs": [
                    {
                        "ContainerSettings": {
                            "Container": "MP4",
                            "Mp4Settings": {}
                        },
                        "VideoDescription": {
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "MaxBitrate": 4500000,
                                    "RateControlMode": "QVBR",
                                    "SceneChangeDetect": "TRANSITION_DETECTION"
                                }
                            }
                        },
                        "AudioDescriptions": [
                            {
                                "AudioSourceName": "Audio Selector 1",
                                "CodecSettings": {
                                    "Codec": "AAC",
                                    "AacSettings": {
                                    "Bitrate": 96000,
                                    "CodingMode": "CODING_MODE_2_0",
                                    "SampleRate": 48000
                                    }
                                }
                            }
                        ]
                    }
                ],
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": f"s3://{BUCKET_NAME}/videos/{only_name}",
                        "DestinationSettings": {
                            "S3Settings": {
                            "StorageClass": "STANDARD"
                            }
                        }
                    }
                }
            }
        ],
        "FollowSource": 1,
        "Inputs": [
            {
                "InputClippings": input_clippings,
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "DefaultSelection": "DEFAULT"
                    }
                },
                "VideoSelector": {},
                "TimecodeSource": "ZEROBASED",
                "FileInput": f"s3://{BUCKET_NAME}/videos/{video_name}"
            }                
        ]
    }        

    response = mediaconvert.create_job(    
        Role=MEDIA_CONVERT_ROLE,
        Settings=settings
    )

    job_id = response['Job']['Id']
    status = response['Job']['Status']
    print(job_id, status)

    while status == 'SUBMITTED' or status == 'PROGRESSING':
        time.sleep(1)
        response = mediaconvert.get_job(Id=job_id)
        status = response['Job']['Status']
        # print(status)

    print(status)

    return shortened_video_name, status
   

def handler(event, context):
    print(event)

    video_name = json.loads(event['body'])['name']
    job_name = str(uuid.uuid4())

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode='ko-KR',
        MediaFormat='mp4',
        Media={
            'MediaFileUri': f's3://{BUCKET_NAME}/videos/{video_name}'
        },
        OutputBucketName=BUCKET_NAME,
        OutputKey=f'subtitles/{job_name}/output.json',
        Subtitles={
            'Formats': ['vtt']
        }
    )

    response = transcribe.get_transcription_job(
        TranscriptionJobName=job_name
    )

    status = response['TranscriptionJob']['TranscriptionJobStatus']
    while status == 'QUEUED' or status == 'IN_PROGRESS':
        print('Transcription in progress...')        
        response = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        time.sleep(10)

    print('Transcription is completed.')

    # 내용 요약 작업 수행
    object_key = f'subtitles/{job_name}/output.json'

    response = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
    content = json.loads(response['Body'].read().decode('utf-8'))

    temp = []
    for transcript in content['results']['transcripts']:
        temp.append(transcript['transcript'])

    transcripts = ' '.join(temp)

    user_prompt = f"<script>{transcripts}</script>"

    system_prompt = """
당신은 비디오 자막 스크립트의 요약 작업을 합니다.
<script> 에는 비디오에서 추출한 자막 스크립트가 있습니다.
<script> 에서 주요 키워드 10개를 추출하고, 요약을 만듭니다.
답변은 JSON 형식으로 출력합니다.
JSON 형식:
{    
    "요약": "요약",
    "주요 키워드": ["키워드", ...]
}

Respond only in korean.
Skip the preamble.
You must respond in a valid JSON format.
You must not wrap JSON response in backticks, markdown, or in any other way, but return it as plain text.
"""
    summary_text = get_response(user_prompt, system_prompt)
    print(summary_text)

    summarization = json.loads(summary_text)

    # 스크립트 요약 작업 수행
    object_key = f'subtitles/{job_name}/output.vtt'

    response = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
    content = response['Body'].read().decode('utf-8')

    user_prompt = f"<script>{content}</script>"

    system_prompt = """<script> 에는 WEBVTT 형식의 자막 스크립트가 있습니다.
<script> 에서 상품을 설명하는 부분만 선별합니다.
선별된 부분은 원본의 형식을 유지합니다.
선별된 부분의 각 스크립트의 시간은 2초를 넘어야 합니다.
선별된 부분을 연결했을 때 각 부분이 겹치지 말아야 하고 시간순으로 정렬되어야 합니다.
선별된 부분의 시간을 다 합치면 60초에서 90초가 되도록 만듭니다.
답변은 WEBVTT형식으로 츨력합니다.

Skip the preamble.
"""
    output = get_response(user_prompt, system_prompt)

    pattern = re.compile(r'(\d{2}:\d{2}:\d{2}.\d{3}) --> (\d{2}:\d{2}:\d{2}.\d{3})')
    tracks = pattern.findall(output)

    shortened_video_name, status = stitching_clips(video_name, tracks)
    print(shortened_video_name, status)

    response = {
        "summary": summarization,
        "shortened": f'videos/{shortened_video_name}'
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
