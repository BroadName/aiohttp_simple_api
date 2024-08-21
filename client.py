import asyncio

import aiohttp


async def main():

    session = aiohttp.ClientSession()
    response = await session.post(
        "http://127.0.0.1:8080/posts",
        json={'title': 'my first post',
              'description': 'test description',
              'author': 'Oleg'},
        )
    print(await response.json())

    response = await session.post(
        "http://127.0.0.1:8080/posts",
        json={'title': 'my post',
              'description': 'rude_word',
              'author': 'Alex'},
    )
    print(await response.json())

    response = await session.patch(
        "http://127.0.0.1:8080/posts/1",
        json={'description': 'rude_word'}
        )
    print(await response.json())

    response = await session.patch(
        "http://127.0.0.1:8080/posts/1",
        json={'description': 'new description'}
    )
    print(await response.json())

    response = await session.get(
        "http://127.0.0.1:8080/posts/1")
    print(await response.json())

    response = await session.delete(
        "http://127.0.0.1:8080/posts/1",
    )
    print(await response.json())

    response = await session.get(
        "http://127.0.0.1:8080/posts/1",
    )
    print(await response.json())
    await session.close()


asyncio.run(main())
