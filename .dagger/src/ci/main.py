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
            with_exec(["uv", "run", "pytest", "-v", "-p", "no:warnings"]).
            stdout()
        )

    @function
    async def test_nsdf_cli(self, source: Annotated[dagger.Directory, DefaultPath("/nsdf_dark_matter_cli"), Doc("nsdf dark matter cli source directory")]) -> str:
        """Test nsdf dark matter library"""
        return (
            await self.build_test_env(source).
            with_exec(["uv", "run", "pytest", "-v"]).
            stdout()
        )

    @function
    def build_test_env(self, source: Annotated[dagger.Directory, DefaultPath("/nsdf_dark_matter"), Doc("source directory to build the test env")]) -> dagger.Container:
        """Build a ready-to-use test environment with UV structure"""
        return (
            dag.container().from_("python@sha256:9e6a62a66f88f5b5be9434fe50af75bcafb8732bafe766a60f5cfc4291470ded").
            with_directory("/src", source, exclude=[".venv", "dist"]).
            with_exec(["pip", "install", "uv"]).
            with_workdir("/src").
            with_exec(["uv", "sync", "--all-groups"])
        )
