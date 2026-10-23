import asyncio
import os

from gen_ai_hub.context_registry import ContextRegistryApiClient, TabularArtifactsApi


async def main() -> None:
    resource_group = os.environ["AICORE_RESOURCE_GROUP"]
    client = ContextRegistryApiClient()
    api = TabularArtifactsApi(client)
    response = await api.get_all_tabular_artifacts()

    artifacts = response.resources or []
    print(f"Found {len(artifacts)} tabular artifact(s) in resource group '{resource_group}':")
    for a in artifacts:
        print(f"  - {a}")


if __name__ == "__main__":
    asyncio.run(main())
