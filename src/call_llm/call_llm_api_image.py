import base64

from zai import ZhipuAiClient

from utils.api_key_util import get_api_key_zhipu_glm


async def call_llm_api_image(text, image_path):
    print(f"使用 API key: {get_api_key_zhipu_glm()} 访问 ZhipuAi 模型 api")
    client = ZhipuAiClient(api_key=get_api_key_zhipu_glm())  # 填写您自己的APIKey
    # 本地图片 需要 base64 编码
    with open(image_path, "rb") as img_file:
        img_base = base64.b64encode(img_file.read()).decode("utf-8")
    response = client.chat.completions.create(
        model="glm-4.6v-flash",  # 填写需要调用的模型名称
        messages=[
            {
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            # 远程图片 url
                            "url": img_base
                        }
                    },
                    {
                        "type": "text",
                        "text": text
                    }
                ],
                "role": "user"
            }
        ],
        thinking={
            "type": "enabled"
        },
        stream=False
    )
    result = response.choices[0].message.content
    print(result)
    return result
