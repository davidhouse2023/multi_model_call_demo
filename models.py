import json
import os
import time

import dashscope
import streamlit as st
import openai
import requests
from typing import Generator
from transformers import AutoTokenizer
from http import HTTPStatus
from dashscope import Generation

os.environ["DASHSCOPE_API_KEY"] = "" # 设置qwen的api key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


class BaseModel:
    def __init__(self,model_name:str):

        self.model_name = model_name

    def response(self)->Generator:

        if self.model_name == 'gpt3.5':
            return self.http_gpt_35()

        elif self.model_name == 'gpt4':
            return self.http_gpt_4()
        elif self.model_name == 'qwen_MAX':
            return self.http_qwen_max()
        elif self.model_name == 'qwen_PLUS':
            return self.http_qwen_plus()
        elif self.model_name == 'qwen-turbo':
            return self.http_qwen_turbo()
        elif self.model_name == 'OurModel':
            return self.http_OurModel()

    def http_gpt_35(self)->Generator:
        """
        Call the dialogue model API
        :param messages: User input
        :return: Generator
        """

        openai.api_type = ""
        openai.api_version = ""
        openai.api_base = ""
        openai.api_key = ""
        stream = openai.ChatCompletion.create(
            engine="gpt35-16k-jp",
            messages=st.session_state[self.model_name],
            stream=True

        )
        st.session_state['cache_assistant'] = ""  # 记录模型回答
        for chunk in stream:
            if chunk.choices and chunk.choices[0] and getattr(chunk.choices[0], "delta") and "content" in chunk.choices[0].delta.keys():
                st.session_state['cache_assistant'] += chunk.choices[0].delta['content']
                yield chunk.choices[0].delta['content']
    def http_gpt_4(self)->Generator:
        """
        Call the dialogue model API
        :param messages: User input
        :return: Generator
        """

        openai.api_type = ""
        openai.api_version = ""
        openai.api_base = ""
        openai.api_key = ""
        stream = openai.ChatCompletion.create(
            engine="gpt-4-jp",
            messages=st.session_state[self.model_name],
            stream=True
        )

        st.session_state['cache_assistant'] = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0] and getattr(chunk.choices[0], "delta") and "content" in chunk.choices[0].delta.keys():
                st.session_state['cache_assistant'] += chunk.choices[0].delta['content']
                yield chunk.choices[0].delta['content']

    def http_qwen_max(self)->Generator:
        responses = Generation.call(
            model="qwen-max-0428",
            messages=st.session_state[self.model_name],
            result_format='message',
            stream=True,
            incremental_output=True
        )
        full_content = ""
        last_data = ''
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                full_content += response.output.choices[0].message.content
                st.session_state['cache_assistant'] = full_content
                output = full_content.replace(last_data, '')
                last_data = full_content
                yield output
    def http_qwen_plus(self)->Generator:
        responses = Generation.call(
            model="qwen-plus",
            messages=st.session_state[self.model_name],
            result_format='message',
            stream=True,
            incremental_output=True
        )
        full_content = ""
        last_data = ''
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                full_content += response.output.choices[0].message.content
                st.session_state['cache_assistant'] = full_content
                output = full_content.replace(last_data, '')
                last_data = full_content
                yield output
    def http_qwen_turbo(self)->Generator:
        responses = Generation.call(
            model="qwen-turbo",
            messages=st.session_state[self.model_name],
            result_format='message',
            stream=True,
            incremental_output=True
        )
        full_content = ""
        last_data = ''
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                full_content += response.output.choices[0].message.content
                st.session_state['cache_assistant'] = full_content
                output = full_content.replace(last_data, '')
                last_data = full_content
                yield output


    def http_OurModel(self)->Generator:
        """
        在这里添加你自己的模型调用
        """
        yield ""

