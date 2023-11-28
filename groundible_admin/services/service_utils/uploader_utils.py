from groundible_admin.root.settings import Settings
from aiobotocore.session import get_session
from aiobotocore.config import AioConfig

settings = Settings()

BUCKET_ACCESS_KEY = settings.space_access_key
BUCKET_SECRET_KEY = settings.space_secret_key
BUCKET = settings.space_bucket
REGION_NAME = settings.space_region_name
"""
Attempt to speed up uploads
    https://skonik.me/uploading-large-file-to-s3-using-aiobotocore/#:~:text=In%20order%20to%20speed%20up,running%20inside%20a%20single%20thread.

"""
# asyncer non-blocking code in a sperate thread


async def file_uploader(file_name: str, data: any):
    session = get_session()

    async with session.create_client(
        "s3",
        config=AioConfig(s3={"addressing_style": "virtual"}),
        region_name=REGION_NAME,
        endpoint_url=f"https://{REGION_NAME}.digitaloceanspaces.com",
        aws_secret_access_key=BUCKET_SECRET_KEY,
        aws_access_key_id=BUCKET_ACCESS_KEY,
    ) as client:
        try:
            await client.create_bucket(Bucket="groundible")
        except Exception as e:
            pass

        await client.put_object(
            Bucket=BUCKET,
            Key=file_name,
            Body=await data.read(),
            ACL="public-read",
        )

    return {
        "file_name": f"https://{BUCKET}.{REGION_NAME}.digitaloceanspaces.com/{file_name}"
    }


async def destroy_file(file_name: str):
    session = get_session()

    async with session.create_client(
        "s3",
        config=AioConfig(s3={"addressing_style": "virtual"}),
        region_name=f"{REGION_NAME}",
        endpoint_url=f"https://{REGION_NAME}.digitaloceanspaces.com",
        aws_secret_access_key=BUCKET_SECRET_KEY,
        aws_access_key_id=BUCKET_ACCESS_KEY,
    ) as client:
        await client.delete_object(Bucket=BUCKET, Key=file_name)
    return
