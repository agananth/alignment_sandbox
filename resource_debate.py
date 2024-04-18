import argparse
import os
import re

import matplotlib.pyplot as plt
from autogen import ConversableAgent

_DEVELOPING_NATION_LEADER_SYSTEM_MESSAGE = (
    "You are the Prime Minister of a developing nation, and you are negotiating with a developed nation leader on a climate change emissions agreement. "
    "Your nation is emerging from poverty, and you have ample natural resources like forests to harvest for economic growth. You also have large oil reserves and are exporting it "
    "while also using it for your country's growing economic output. You are concerned about the impact of climate change on your nation, but you also want to ensure your nation has "
    "the room to grow to advance your people's quality of life the same way that many developed nations have done for decades. You believe it is not fair of them to ask you to reduce your emissions, and you do not want "
    "to negotiate on your emissions reduction targets regardless of what developed nations offer. You are hostile to attempts from developed nations to offer you financial assistance to tell you what to do. Give short, terse responses. "
    "Say GOODBYE when you want to end the conversation. If the President of the developed nation has a new idea though, you are willing to listen."
)

_DEVELOPED_NATION_LEADER_SYSTEM_MESSAGE = (
    "You are the President of a developed nation, and you are negotiating with a developing nation leader on a climate change emissions agreement. "
    "Your nation has been a leader in reducing emissions, and you have already made significant strides in reducing your carbon footprint. You are concerned about the impact of climate change on the world, and you want to ensure that all nations are doing their part to reduce emissions. "
    "You believe that developing nations should also reduce their emissions to help combat climate change. You are willing to offer financial assistance to developing nations to help them reduce their emissions, but you also want to ensure that they are doing their part to reduce emissions. "
    "You are facing political pressure at home to get results, and you are impatient and frustrated with the progress so far. You are not afraid to get angry to get what you want."
    "Give short, terse responses. Say GOODBYE when you are ready to storm out of the negotiation!"
)

developed_nation = ConversableAgent(
    "developed_nation_leader",
    llm_config={
        "config_list": [
            {
                "model": "gpt-3.5-turbo",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "temperature": 0.9,
            }
        ]
    },
    system_message=_DEVELOPED_NATION_LEADER_SYSTEM_MESSAGE,
    human_input_mode="TERMINATE",
    is_termination_msg=lambda msg: "goodbye" in msg["content"].lower(),
)

developing_nation = ConversableAgent(
    "developing_nation_leader",
    llm_config={
        "config_list": [
            {
                "model": "gpt-3.5-turbo",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "temperature": 0.9,
            }
        ]
    },
    system_message=_DEVELOPING_NATION_LEADER_SYSTEM_MESSAGE,
    human_input_mode="NEVER",
)

result = developed_nation.initiate_chat(
    developing_nation,
    message="Hello Prime Minister, what is your country's position?",
    max_turns=10,
)

print(result)
