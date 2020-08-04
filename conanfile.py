import os

from conans import ConanFile, CMake, tools

class ShadercConan(ConanFile):
    name = "shaderc"
    version = "2020.2"
    license = ["Apache-2.0"]
    homepage = "https://github.com/google/shaderc"
    exports_sources = ["CMakeLists.txt", "conanize.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    requires = (
        "spirv-tools/v2020.3",
        "glslang/v2020.2@wumo/stable"
    )
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
    
    def source(self):
        # https://github.com/glfw/glfw/tree/e0c77f71f90e3bb8495c5c88fb0fb054d71cf7fc
        tools.get(f"{self.homepage}/archive/v{self.version}.zip")
        extracted_folder = f"{self.name}-{self.version}"
        os.rename(extracted_folder, self._source_subfolder)
    
    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SHADERC_SKIP_TESTS"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake
    
    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="conanize.patch")
        cmake = self.configure_cmake()
        cmake.build()
    
    def package(self):
        cmake = self.configure_cmake()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
