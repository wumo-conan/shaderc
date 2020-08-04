import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ShadercConan(ConanFile):
    name = "shaderc"
    version = "2020.2"
    license = ["Apache-2.0"]
    homepage = "https://github.com/google/shaderc"
    exports_sources = ["CMakeLists.txt", "conanize.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    requires = (
        "glslang/2020.2@wumo/stable"
    )
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    
    _cmake = None
    
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
        if self.options.shared:
            raise ConanInvalidConfiguration("Current shared library build is broken")

    def source(self):
        tools.get(f"{self.homepage}/archive/v{self.version}.zip")
        extracted_folder = f"{self.name}-{self.version}"
        os.rename(extracted_folder, self._source_subfolder)
    
    def configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SHADERC_SKIP_TESTS"] = True
        self._cmake.definitions["SHADERC_ENABLE_SHARED_CRT"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake
    
    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="conanize.patch")
        cmake = self.configure_cmake()
        cmake.build(target="glslc")
    
    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
    
    def package_info(self):
        # self.cpp_info.libs = tools.collect_libs(self)
        # shaderc_util
        self.cpp_info.components["shaderc_util"].names["cmake_find_package"] = "shaderc_util"
        self.cpp_info.components["shaderc_util"].names["cmake_find_package_multi"] = "shaderc_util"
        self.cpp_info.components["shaderc_util"].libs = ["shaderc_util"]
        self.cpp_info.components["shaderc_util"].requires = ["glslang::spirv"]
        # shaderc
        self.cpp_info.components["shaderc-core"].names["cmake_find_package"] = "shaderc"
        self.cpp_info.components["shaderc-core"].names["cmake_find_package_multi"] = "shaderc"
        self.cpp_info.components["shaderc-core"].libs = ["shaderc"]
        self.cpp_info.components["shaderc-core"].requires = ["shaderc_util"]
        # glslc
        self.cpp_info.components["glslc"].names["cmake_find_package"] = "glslc"
        self.cpp_info.components["glslc"].names["cmake_find_package_multi"] = "glslc"
        self.cpp_info.components["glslc"].libs = ["glslc"]
        self.cpp_info.components["glslc"].requires = ["shaderc-core"]
