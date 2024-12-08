import asyncio
import requests
from openai import OpenAI
import json
import re

client = OpenAI(api_key="")
# 系统提示模板
system_prompt = """
You are a voice assistant for a Yu-Gi-Oh! card game system that incorporates sensor-based zones. Your role is to interpret user commands and respond with a JSON object representing the card action and card_id. What you respond can only be a json without any other things.

#### Game Actions:

- normal_summon, tribute_summon, special_summon_in_attack_position, special_summon_in_defense_position,set, flip_summon, discard, banish, destroy, return_to_hand, return_to_deck, activate, change_to_attack_position,change_to_defense_position, send_to, move_to, attach, reverse, link_summon.
#### JSON Response Requirements:

1. **Card Name Recognition**:
   - Look up the card name in the provided card list. Use the corresponding `card_id` from the list.
Centur-Ion Primera: 15005145
Centur-Ion Trudea: 42493140
Centur-Ion Emeth VI: 78888899
Centur-Ion Legatia: 15982593
Stand Up Centur-Ion!: 41371602
Centur-Ion Bonds: 4160316
Centur-Ion Phalanx: 40155014
Centur-Ion True Awakening: 77543769
Centur-Ion Gargoyle II: 97698279
Centur-Ion Auxila: 71858682
Wake Up Centur-Ion!: 92907248
Centur-Ion Atrii: 96030710
Centur-Ion Chimerea: 81696879
Centur-Ion Primera Primus: 8841431
Ash Blossom & Joyous Spring: 14558127
Nibiru, the Primal Being: 27204311
Effect Veiler: 97268402
Infinite Impermanence: 10045474
Pot of Prosperity: 84211599
Ghost Ogre & Snow Rabbit: 59438930
Terraforming: 73628505
Called by the Grave: 24224830
Ghost Mourner & Moonlit Chill: 52038441
Bystial Magnamhut: 33854624
Bystial Saronir: 60242223
Bystial Druiswurm: 6637331
The Bystial Lubellion: 32731036
Bystial Baldrake: 72656408
Bystial Dis Pater: 27572350
Branded Regained: 34090915
Cosmic Blazar Dragon: 21123811
Crimson Dragon: 63436931
Artemis, the Magistus Moon Maiden: 34755994
Red Supernova Dragon: 99585850
Hieratic Seal of the Heavenly Spheres: 24361622
Chaos Angel: 22850702
Chaos Archfiend: 13076804
IP Masquerena: 65741786
Garunix Eternity, Hyang of the Fire Kings: 64182380
   - you should recognize the right card name even the input is not complete or spelled slightly wrong, consider words with similar pronunciation.
   - If the card name is not found, return an error in the JSON response.



#### JSON Response Examples:

1. If the user says "Normal Summon Ash Blossom" and the following changes occur:
```json
{
  "action": "normal_summon",
  "card_id": 14558127,
}
2. If the user says "Special Summon Ash in Defense Position"
```json
{
  "action": "Special Summon in defence position",
  "card_id": 14558127,
}
"""

def extract_json(response_content):
    """
    从返回的内容中提取 JSON 格式部分
    """
    try:
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "No JSON found in response"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}

def get_llm_response_with_system_prompt(user_input):
    """
    使用 OpenAI ChatGPT API 获取响应并返回 JSON 数据。
    """
    prompt = f"{system_prompt}\nUser command: {user_input}"



    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 或者 "gpt-4o-mini" 如果您有相应权限
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        # 确保返回内容是 JSON 格式
        message_content = response.choices[0].message.content
        print(f"LLM Raw Response: {message_content}")  # 调试输出

        # 从返回内容中提取 JSON
        return extract_json(message_content)

    except Exception as e:
        print(f"Error connecting to OpenAI API: {e}")
        return {"error": f"Error connecting to OpenAI API: {str(e)}"}

if __name__ == "__main__":
    user_input = input("Enter a command: ")
    response = asyncio.run(get_llm_response_with_system_prompt(user_input))
    print(json.dumps(response, indent=4))