import json

# 現有的 JSON 字符串
json_str = '''
{
    "username": "_meowww_",
    "user_id": 253922578790350848,
    "discriminator": "0",
    "api_keys": {
        "api_key": "api_key",
        "secret": "secret",
        "password": "password"
    },
    "choice": "SOL"
}
'''

# 將 JSON 字符串轉換為字典
data = json.loads(json_str)

# 添加新屬性
data['new_attribute'] = 'new_value'

# 如果需要，將更新後的字典轉換回 JSON 字符串
updated_json_str = json.dumps(data, indent=4)

print(updated_json_str)