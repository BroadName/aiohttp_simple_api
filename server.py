import json

from aiohttp import web
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Post, init_orm, engine, Session
from sqlalchemy.ext.asyncio import AsyncSession

from schema import PostCreate, PostUpdate


app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await engine.dispose()
    print("SHUTDOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def validate(json_data, schema_cls):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop('ctx', None)
        raise get_error(errors[0].get('msg'), web.HTTPBadRequest)


def get_error(message: dict | list | str, err_cls):
    return err_cls(
            text=json.dumps({'error': message}),
            content_type="application/json"
        )


async def get_post(session: AsyncSession, post_id) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise get_error("user not found", web.HTTPNotFound)
    return post


async def add_post(session: AsyncSession, post: Post):
    session.add(post)
    try:
        await session.commit()
    except IntegrityError:
        raise get_error("post with this title already exist", web.HTTPConflict)


class PostsView(web.View):

    @property
    def post_id(self):
        return int(self.request.match_info['post_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get(self):
        post = await get_post(self.session, self.post_id)
        return web.json_response(post.json)

    async def post(self):
        json_data = validate(await self.request.json(), PostCreate)
        post = Post(**json_data)
        await add_post(self.session, post)
        return web.json_response({'id': post.id})

    async def patch(self):
        json_data = validate(await self.request.json(), PostUpdate)
        post = await get_post(self.session, self.post_id)
        for field, value in json_data.items():
            setattr(post, field, value)
        await add_post(self.session, post)
        return web.json_response(post.json)

    async def delete(self):
        post = await get_post(self.session, self.post_id)
        await self.session.delete(post)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})


app.add_routes(
    [
        web.post("/posts", PostsView),
        web.get("/posts/{post_id:\d+}", PostsView),
        web.patch("/posts/{post_id:\d+}", PostsView),
        web.delete("/posts/{post_id:\d+}", PostsView)
    ]
)


def main():
    web.run_app(app)


if __name__ == "__main__":
    main()

