from conans import ConanFile, CMake, tools

class UHEMesh(ConanFile):
    name = "UHEMesh"
    version = "0.4.2"
    license = "MIT"
    url = "https://github.com/Ubpa/UHEMesh"
    description = "Ubpa Container"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports_sources = "patches/*"
    requires = "UContainer/0.0.6"

    def source(self):
        self.run("git clone https://github.com/Ubpa/UHEMesh.git --branch 0.4.2 --depth 1")

        # TODO: find a elegent way of copying
        content = tools.load("patches/UbpaEssential.cmake")
        tools.save("UHEMesh/UbpaEssential.cmake", content)
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly

#         tools.replace_in_file("UHEMesh/CMakeLists.txt", "PROJECT(MyHello)",
#                               '''PROJECT(MyHello)
# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup()''')


        tools.replace_in_file("UHEMesh/CMakeLists.txt", "include(cmake/InitUCMake.cmake)", "")
        tools.replace_in_file("UHEMesh/CMakeLists.txt", "Ubpa_InitUCMake()", "")
        tools.replace_in_file("UHEMesh/CMakeLists.txt", "Ubpa_InitProject()", "include(UbpaEssential.cmake)")
        tools.replace_in_file("UHEMesh/CMakeLists.txt", "Ubpa_AddDep(UContainer 0.0.6)", '''
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(NAMESPACED_CONAN_DEPENDENCIES ${CONAN_DEPENDENCIES})
list(TRANSFORM NAMESPACED_CONAN_DEPENDENCIES PREPEND "CONAN_PKG::")
''')
        tools.replace_in_file("UHEMesh/CMakeLists.txt", 'Ubpa_Export(DIRECTORIES "include")', "")
        tools.replace_in_file("UHEMesh/src/EMPTY/CMakeLists.txt", "Ubpa::UContainer_core", "CONAN_PKG::UContainer")
        tools.replace_in_file("UHEMesh/src/EMPTY/CMakeLists.txt", "${core}", "${core} ${NAMESPACED_CONAN_DEPENDENCIES}")
        tools.replace_in_file("UHEMesh/src/test/00_basic/CMakeLists.txt", "${core}", "${core} ${NAMESPACED_CONAN_DEPENDENCIES}")
        


    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="UHEMesh")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="UHEMesh/include")
        self.copy("*.inl", dst="include", src="UHEMesh/include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = []