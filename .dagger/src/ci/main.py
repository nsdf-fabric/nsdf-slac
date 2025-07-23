from typing import Annotated
import dagger
from dagger import dag, function, object_type, DefaultPath, Doc


@object_type
class Ci:
    @function
    async def test_nsdf_library(self, source: Annotated[dagger.Directory, DefaultPath("/nsdf_dark_matter"), Doc("nsdf dark matter library source directory")]) -> str:
        """Test nsdf dark matter library"""
        return (
            await self.build_test_env(source).
            with_workdir("src/tests").
            with_exec(["uv", "run",  "test_idx_dark_matter.py"]).
            stdout()
        )

    @function
    def build_test_env(self, source: Annotated[dagger.Directory, DefaultPath("/nsdf_dark_matter"), Doc("source directory to build the test env")]) -> dagger.Container:
        """Build a ready-to-use test environment with UV structure"""
        return (
            dag.container().from_("python:3.10-slim").
            with_directory("/src", source, exclude=[".venv", "dist"]).
            with_exec(["pip", "install", "uv"]).
            with_workdir("/src").
            with_exec(["uv", "sync"])
        )
