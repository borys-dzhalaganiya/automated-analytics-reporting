import requests

url = 'https://jsonplaceholder.typicode.com/posts/1'

response = requests.get(url, timeout=10)

print(response.status_code)
print(response.json())

data = response.json()
print(data['title'])
print(type(data))

post_url = 'https://jsonplaceholder.typicode.com/posts'

payload = {
    'source': 'facebook',
    'change': -747623,
    'month': '2026-09'
}

response_post = requests.post(post_url, json=payload, timeout=10)
print(response_post.status_code)
print(response_post.json())

response_post.raise_for_status()

result = response_post.json()

print(result['change'])
print(type(result['change']))
