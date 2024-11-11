import json
import logging
import time
from functools import partial
from io import StringIO

import traceback

import streamlit as st
from models import BaseModel


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
time_hold = 12

# TODO 在这里添加你的模型
model_pool=["gpt3.5","gpt4","qwen_MAX","qwen_PLUS","qwen-turbo","OurModel"]


system_content = """你是一个聪明的对话机器人！"""


def page_base_setting():
    """
    Some basic configurations for setting page styles
    Including logo, title, buttons, etc
    """
    img = './LOGO.png'
    # Sidebar Settings
    with st.sidebar:
        st.image(
            img,  # 图片路径或URL
            width=300  # 调整图片宽度，单位为像素
        )
        # New round of dialogue button
        btn_NewRound = st.button("New Round", type="primary")

        if btn_NewRound:
            st.session_state['messages'] = []
            for item in st.session_state['model_list']:
                st.session_state[item] =st.session_state[item][:1]

        txt=st.text_area("please modify your prompt template here👇",value=system_content,height=500)
        if txt:
            try:
                st.session_state[
                    'prompt'] = txt
                for item in st.session_state['model_list']:
                    for state in st.session_state[item]:
                        if ("role", "system") in state.items():
                            state["content"] = st.session_state['prompt']
            except Exception as e:
                error=traceback.format_exc()
                st.error(error)

    # Set the main interface title
    st.subheader("Please select the model you want to use 🐱‍💻:")
    # Set button style
    st.markdown("""
                    <style>
                    .stButton > button {
                        width: 100%;  /* 设置按钮宽度为100% */
                    }
                    .footer {
                        position: fixed;
                        left: 0;
                        bottom: 0;
                        width: 100%;
                        background-color: white;
                        padding: 10px 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)


def click_button(model_name:str):
    """
    :param model_name:
    :return:
    """
    # update the model list
    st.session_state['model_list'] = [model_name]
    temp=[]
    for dialog in st.session_state.messages:
        if dialog["role"] == "user" or dialog["role"] == model_name:
            temp.append(dialog)
    # update the messages
    st.session_state['messages']=temp
    # update the checkbox status
    for i in model_pool:
        if i==model_name:
            st.session_state[i + 'checked']=True
        else:
            st.session_state[i + 'checked']=False

def process_answer(prompt:str):
    """
    :param prompt: user input
    :return:
    """
    if prompt:
        with st.chat_message("user", avatar='🧐'):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        # display all model dialogs
        for model_name in st.session_state.model_list:
            model = BaseModel(model_name)
            with st.chat_message(model_name):
                messages = []
                for item in st.session_state.messages:
                    if item["role"] == "user" or item["role"] == model_name:
                        messages.append(item)
                st.session_state[model_name].append({"role": "user", "content": prompt})
                # st.write("--被动回答--" + model_name + '\n\n')
                st.write( model_name + '\n\n')
                st.write_stream(model.response())
                st.session_state[model_name].append(
                    {"role": "assistant", "content": st.session_state['cache_assistant']})
                logger.info(model_name + ':' + json.dumps(st.session_state[model_name], indent=2, ensure_ascii=False))
                st.session_state.messages.append({"role": model_name, "content": st.session_state['cache_assistant']})

    else:
        prompt="用户没有及时反馈,你需要主动回答"
        # display all model dialogs
        for model_name in st.session_state.model_list:
            model = BaseModel(model_name)
            with st.chat_message(model_name):
                messages = []
                for item in st.session_state.messages:
                    if item["role"] == "user" or item["role"] == model_name:
                        messages.append(item)
                st.session_state[model_name][-1]["content"] += prompt
                logger.info(model_name + ':' + json.dumps(st.session_state[model_name], indent=2, ensure_ascii=False))
                st.write("--主动回答--" + model_name + '\n\n')
                st.write_stream(model.response())
                st.session_state[model_name].append(
                    {"role": "assistant", "content": st.session_state['cache_assistant']})
                st.session_state.messages.append({"role": model_name, "content": st.session_state['cache_assistant']})



        if len(st.session_state.model_list) > 1:
            footer = st.empty()
            with footer.container():
                prefer_model = None
                for index, col in enumerate(st.columns(len(st.session_state.model_list))):
                    with col:
                        text = "Prefer " + st.session_state.model_list[index] + " ♥"
                        st.button(text, type="primary", key=index,
                                  on_click=partial(click_button, model_name=st.session_state.model_list[index]))



if __name__ == '__main__':

    # model list
    if 'model_list' not in st.session_state:
        st.session_state['model_list'] = []
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = []
    st.session_state['last_prompt'] = None

    # Configure page basic style
    page_base_setting()

    #  user input
    prompt = st.chat_input("Enter you question")
    logger.info(prompt)
    # head container
    container_head = st.container(border=True)

    with container_head:
        temp = []
        for index, col in enumerate(st.columns(len(model_pool), gap="small")):
            # checkbox status
            if model_pool[index]+'checked' not in st.session_state:
                st.session_state[model_pool[index]+'checked']=False

            with col:
                res=st.checkbox(model_pool[index],value=st.session_state[model_pool[index]+'checked'])
                st.session_state[model_pool[index]+'checked']=res
                if res:
                    temp.append(model_pool[index])
        # the model of user select
        st.session_state['model_list']=temp

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # initial messages
    for item in st.session_state['model_list']:
        if item not in st.session_state:
            st.session_state[item] = []
            st.session_state[
                'prompt'] = system_content
            st.session_state[item].append({"role": "system", "content": st.session_state['prompt']})

    # display history messages
    for dialog in st.session_state['messages']:
        if dialog["role"] == "user":
            st.chat_message(dialog["role"], avatar='🧐').write(dialog["content"])
        else:
            st.chat_message(dialog["role"]).write(dialog["content"])

    # process user input
    if len(st.session_state.model_list) > 0:
        if prompt and prompt != st.session_state['last_prompt']:
            st.session_state['last_prompt'] = prompt
            process_answer(prompt)
        start_time = time.time()
        # 主动回答
        # while prompt == st.session_state['last_prompt'] or not prompt:
        #     is_hit = False
        #     end_time = time.time()
        #     if end_time - start_time > time_hold:
        #         process_answer('')
        #         is_hit = True
        #     if is_hit:
        #         break

    else:
        st.info('Please select one or more model first !!! ', icon="🚨")

    logger.info(prompt)
    logger.info(st.session_state['last_prompt'])