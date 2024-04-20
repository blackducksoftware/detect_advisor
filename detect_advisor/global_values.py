#
# Constants
advisor_version = "1.0.5"
detect_version = "9.X.0"

ext_list = {
    'src': ['.4th', '.actionscript', '.ada', '.adb', '.ads', '.aidl', '.as', '.as8', '.asm', '.asp', '.aspx', '.aug',
            '.awk', '.bas', '.bash', '.bat', '.bf', '.bfpp', '.bi', '.bms', '.bmx', '.boo', '.c', '.c#', '.c++',
            '.cbl', '.cc', '.cfc', '.cfm', '.cgi', '.chai', '.clj', '.cljc', '.cljs', '.cls', '.cmd', '.com', '.cpp',
            '.cpy', '.cs', '.cu', '.cuh', '.cxx', '.d', '.dpk', '.dylan', '.e', '.ec', '.eh', '.el', '.erl', '.es',
            '.exec', '.exheres-0', '.exlib', '.f', '.f77', '.f90', '.factor', '.for', '.fpp', '.fr', '.frag', '.frm',
            '.frx', '.fs', '.g77', '.g90', '.glsl', '.go', '.groovy', '.gs', '.h', '.h++', '.haml', '.hh', '.hpp',
            '.hrl', '.hs', '.hx', '.hxx', '.i', '.i3', '.idl', '.inc', '.java', '.js', '.jsp', '.jws', '.l',
            '.lhs', '.lisp', '.lsp', '.lua', '.m', '.m2', '.m3', '.m4', '.ml', '.mli', '.mm', '.mod', '.nb', '.nbs',
            '.octave', '.pas', '.php', '.php3', '.php4', '.php5', '.phps', '.phtml', '.pl', '.pm', '.pp', '.py', '.r',
            '.r3', '.rb', '.rc', '.reb', '.rebol', '.rexx', '.ru', '.s', '.sc', '.scala', '.scm', '.sh', '.sqb',
            '.sql', '.ss', '.st', '.swift', '.tcl', '.tk', '.v', '.vb', '.vba', '.vbe', '.vbs', '.vert', '.vhd',
            '.vhdl', '.vim', '.y', '.z80'],
    'bin': ['.dll', '.obj', '.o', '.a', '.lib', '.iso', '.qcow2', '.vmdk', '.vdi',
            '.ova', '.nbi', '.vib', '.exe', '.img', '.bin', '.apk', '.aac', '.ipa', '.msi'],
    'arc': ['.zip', '.gz', '.tar', '.xz', '.lz', '.bz2', '.7z', '.rar', '.rar',
            '.cpio', '.Z', '.lz4', '.lha', '.arj'],
    'jar': ['.jar', '.ear', '.war'],
    'zip': ['.jar', '.ear', '.war', '.zip'],
    'pkg': ['.rpm', '.deb', '.dmg', '.pki'],
    'lic': ['LICENSE', 'LICENSE.txt', 'notice.txt', 'license.txt', 'license.html', 'NOTICE', 'NOTICE.txt',
            'COPYRIGHTS', 'COPYRIGHTS.txt']
}

sig_excludes = ['.git', '.gradle', 'gradle', 'node_modules', '.synopsys']

det_excludes = ['__MACOX', 'bin', 'build', '.yarn', 'out', 'packages', 'target']
# Added to sig_excludes

pm_dict = {
    'BAZEL':
        {
            'files': [],
            'exts': ['.bzl'],
            'execs': ['bazel'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.bazel.path=PATH_TO_BAZEL\n" +
                "    (OPTIONAL Path to bazel executable.)\n" +
                "--detect.bazel.cquery.options='OPTION1,OPTION2'\n" +
                "    (OPTIONAL List of additional options to pass to the bazel cquery command.)\n" +
                "--detect.bazel.workspace.rules=<ALL, NONE, MAVEN_JAR, MAVEN_INSTALL, HASKELL_CABAL_LIBRARY, HTTP_ARCHIVE>\n" +
                "    (OPTIONAL Bazel workspace external dependency rule: The Bazel workspace rule used to pull in external dependencies.\n" +
                "    If not set, Detect will attempt to determine the rule from the contents of the WORKSPACE file (default: NONE).)\n",
            'cli_reqd':
                "--detect.bazel.target='TARGET'\n" + \
                "    (REQUIRED Bazel Target: The Bazel target (for example, //foo:foolib) for which dependencies are collected.)\n",
        },
    
    'BITBAKE':
        {
            'files': ['oe-init-build-env'],
            'exts': [],
            'execs': ['bitbake'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'linux_only': True,
            'cli_options':
                "--detect.bitbake.package.names='PACKAGE1,PACKAGE2'\n" +
                "    (OPTIONAL List of package names from which dependencies are extracted.)\n" +
                "--detect.bitbake.search.depth=X\n" +
                "    (OPTIONAL The depth at which Detect will search for the recipe-depends.dot or package-depends.dot files (default: 1).)\n" +
                "--detect.bitbake.source.arguments='ARG1,ARG2,ARG3'\n" +
                "    (OPTIONAL List of arguments to supply when sourcing the build environment init script)\n",
                "--detect.bitbake.dependency.types.excluded=<NONE, BUILD>\n" +
                "    (OPTIONAL List of package names from which dependencies are extracted - default NONE.)\n" +
            'cli_reqd':
                "--detect.bitbake.build.env.name=NAME\n" +
                "    (REQUIRED BitBake Init Script Name: The name of the build environment init script (default: oe-init-build-env).)\n"
        },
    
    'CARGO':
        {
            'files': ['Cargo.toml'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Cargo.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'CARTHAGE':
        {
            'files': ['Cartfile'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Cartfile.resolved'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'CLANG':
        {
            'files': ['compile_commands.json'],
            'exts': [],
            'execs': ['clang'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'linux_only': True,
            'cli_options':
                "    Detect supports reading a compile_commands.json file generated by cmake.\n" +
                "    However, it may be better to use the https://pypi.org/project/blackduck-c-cpp utility to scan C/C++ projects\n" +
                "    which runs a full build scan\n",
        },
    
    'COCOAPODS':
        {
            'files': ['Podfile.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Podfile.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'CONAN':
        {
            'files': ['conanfile.txt', 'conanfile.py'],
            'exts': [],
            'execs': ['conan'],
            'exec_reqd': False,
            'lock_files': ['conan.lock'],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.conan.path=PATH_TO_CONAN\n" +
                "    (OPTIONAL Path to conan executable.)\n" +
                "--detect.bitbake.dependency.types.excluded=<NONE, BUILD>\n" +
                "    (OPTIONAL Exclude dev dependencies - default NONE.)\n" +
                "--detect.conan.arguments='ARG1 ARG2'\n" +
                "    (OPTIONAL List of additional options to pass to the conan command.)\n" +
                "--detect.conan.lockfile.path=PATH\n" +
                "    (OPTIONAL The path to the conan lockfile to apply when running 'conan info' to get the dependency graph.)\n" +
                "--detect.conan.attempt.package.revision.match=<true, false>\n" +
                "     (OPTIONAL Attempt Package Revision Match: If package revisions are available (a Conan lock file is found or provided, and Conan's revisions feature is enabled), require that each dependency's package revision match the package revision of the component in the KB.)\n"
        },
    
    'CONDA':
        {
            'files': ['environment.yml'],
            'exts': [],
            'execs': ['conda'],
            'lock_files': [],
            'lockfile_reqd': False,
            'exec_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.conda.path=PATH_TO_CONDA\n" +
                "    (OPTIONAL Path to conda executable)\n" +
                "--detect.conda.environment.name=NAME\n" +
                "    (OPTIONAL The name of the anaconda environment used by your project)\n",
        },
    
    'CPAN':
        {
            'files': ['Makefile.PL'],
            'exts': [],
            'execs': ['cpan', 'cpanm'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.cpan.path=PATH_TO_CPAN\n" +
                "    (OPTIONAL Path to cpan executable.)\n" +
                "--detect.cpanm.path=PATH_TO_CPANM\n" +
                "    (OPTIONAL Path to cpanm executable.)\n"
        },
    
    'CPP':
        {
            'files': ['makefile', 'CMakeLists.txt'],
            'exts': ['.mk'],
            'execs': ['cpp'],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "    C/C++ projects built using a compiler should be scanned using the blackduck_c_cpp utility.\n" + \
                "    See https://pypi.org/project/blackduck-c-cpp.\n",
        },
    
    'CRAN':
        {
            'files': ['packrat.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['packrat.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'DART':
        {
            'files': ['pubspec.yaml'],
            'exts': [],
            'execs': ['dart', 'flutter'],
            'exec_reqd': False,
            'lock_files': ['pubspec.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.dart.path=PATH_TO_DART\n" +
                "    (OPTIONAL The path to the dart executable.)\n"
                "--detect.flutter.path=PATH_TO_FLUTTER\n" +
                "    (OPTIONAL The path to the flutter executable.)\n" +
                "--detect.pub.dependency.types.excluded=<NONE, DEV>\n" +
                "    (OPTIONAL Exclude dev dependencies - default NONE.)\n"
        },
    
    'GO_DEP':
        {
            'files': ['Gopkg.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Gopkg.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.go.path=PATH_TO_GO\n" +
                "    (OPTIONAL Path to the Go executable.)\n" +
                "--detect.go.mod.dependency.types.excluded=<NONE, UNUSED, VENDORED>\n" +
                "    (OPTIONAL Go Mod Dependency Types Excluded: Set this value to indicate which Go Mod dependency types Detect should exclude from the BOM.)\n"
        },

    'GO_GRADLE':
        {
            'files': ['gogradle.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['gogradle.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.go.path=PATH_TO_GO\n" +
                "    (OPTIONAL Path to the Go executable.)\n" +
                "--detect.go.mod.dependency.types.excluded=<NONE, UNUSED, VENDORED>\n" +
                "    (OPTIONAL Go Mod Dependency Types Excluded: Set this value to indicate which Go Mod dependency types Detect should exclude from the BOM.)\n"
        },

    'GO_MOD':
        {
            'files': ['go.mod'],
            'exts': [],
            'execs': ['go'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.go.path=PATH_TO_GO\n" +
                "    (OPTIONAL Path to the Go executable.)\n" +
                "--detect.go.mod.dependency.types.excluded=<NONE, UNUSED, VENDORED>\n" +
                "    (OPTIONAL Go Mod Dependency Types Excluded: Set this value to indicate which Go Mod dependency types Detect should exclude from the BOM.)\n"
        },

    'GO_VENDOR':
        {
            'files': ['vendor.json'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.go.path=PATH_TO_GO\n" +
                "    (OPTIONAL Path to the Go executable.)\n" +
                "--detect.go.mod.dependency.types.excluded=<NONE, UNUSED, VENDORED>\n" +
                "    (OPTIONAL Go Mod Dependency Types Excluded: Set this value to indicate which Go Mod dependency types Detect should exclude from the BOM.)\n"
        },

    'GO_VNDR':
        {
            'files': ['vendor.conf'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.go.path=PATH_TO_GO\n" +
                "    (OPTIONAL Path to the Go executable.)\n" +
                "--detect.go.mod.dependency.types.excluded=<NONE, UNUSED, VENDORED>\n" +
                "    (OPTIONAL Go Mod Dependency Types Excluded: Set this value to indicate which Go Mod dependency types Detect should exclude from the BOM.)\n"
        },

    'GRADLE':
        {
            'files': ['build.gradle', 'build.gradle.kts'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
            'cli_options':
                "--detect.gradle.path=PATH_TO_GRADLE\n" +
                "    (OPTIONAL Path to the gradle or gradlew executable.)\n" +
                "detect.gradle.configuration.types.excluded=<NONE, UNRESOLVED>\n" +
                "    (OPTIONAL Gradle Configuration Types Excluded: Set this value to indicate which Gradle configuration types Detect should exclude from the BOM.)\n" +
                "--detect.gradle.build.command='ARGUMENT1 ARGUMENT2'\n" +
                "    (OPTIONAL Gradle Build Command: Gradle command line arguments to add to the mvn/mvnw command line.)\n" +
                "--detect.gradle.excluded.configurations='CONFIG1,CONFIG2'\n" +
                "    (OPTIONAL Gradle Exclude Configurations: List of Gradle configurations to exclude.)\n" +
                "--detect.gradle.excluded.projects='PROJECT1,PROJECT2'\n" +
                "    (OPTIONAL Gradle Exclude Projects: List of Gradle sub-projects to exclude.)\n" +
                "--detect.gradle.included.configurations='CONFIG1,CONFIG2'\n" +
                "    (OPTIONAL Gradle Include Configurations: List of Gradle configurations to include.)\n" +
                "--detect.gradle.included.projects='PROJECT1,PROJECT2'\n" +
                "    (OPTIONAL Gradle Include Projects: List of Gradle sub-projects to include.)\n" +
                "--detect.gradle.included.project.paths=PATH\n" +
                "    (OPTIONAL Gradle Include Project Paths: A comma-separated list of Gradle subproject paths to include.)\n"
        },
    
    'HEX':
        {
            'files': ['rebar.config'],
            'exts': [],
            'execs': ['rebar3'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.hex.rebar3.path=PATH_TO_REBAR3\n" +
                "    (OPTIONAL Path to the rebar3 executable.)\n"
        },
    
    'IVY':
        {
            'files': ['ivy.xml'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
        },
    
    'LERNA':
        {
            'files': ['lerna.json'],
            'exts': [],
            'execs': ['lerna'],
            'exec_reqd': True,
            'lock_files': ['package-lock.json', 'npm-shrinkwrap.json', 'yarn.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.lerna.path=PATH_TO_LERNA\n" +
                "    (OPTIONAL Lerna Executable: Path of the lerna executable.)\n" +
                "--detect.lerna.package.types.excluded=<NONE, PRIVATE>\n" +
                "    (OPTIONAL Lerna Package Types Excluded: Set this value to indicate which Lerna package types Detect should exclude from the BOM.)\n" +
                "--detect.lerna.excluded.packages=PACKAGE1,PACKAGE2\n" +
                "    (OPTIONAL Lerna Packages Excluded: A comma-separated list of Lerna packages to exclude.\n" +
                "--detect.lerna.included.packages=PACKAGE1,PACKAGE2\n" +
                "    (OPTIONAL Lerna Packages Included: A comma-separated list of Lerna packages to include.)\n"
        },
    
    'MAVEN':
        {
            'files': ['pom.xml', 'pom.groovy'],
            'exts': [],
            'execs': ['mvn', 'mvnw'],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
            'cli_options':
                "--detect.maven.path=PATH_TO_MAVEN\n" +
                "    (OPTIONAL Path of the Maven executable.)\n" +
                "--detect.maven.build.command='ARGUMENT1 ARGUMENT2'\n" +
                "    (OPTIONAL Maven Build Command: Maven command line arguments to add to the mvn/mvnw command line.)\n" +
                "--detect.maven.excluded.scopes='SCOPE1,SCOPE2'\n" +
                "    (OPTIONAL Dependency Scope Excluded: List of Maven scopes. Output will be limited to dependencies outside these scopes (overrides include).)\n" +
                "--detect.maven.included.scopes='SCOPE1,SCOPE2'\n" +
                "    (OPTIONAL Dependency Scope Included: List of Maven scopes. Output will be limited to dependencies within these scopes (overridden by exclude).)\n" +
                "--detect.maven.excluded.modules='MODULE1,MODULE2'\n" +
                "    (OPTIONAL Maven Modules Excluded: List of Maven modules (sub-projects) to exclude.)\n" +
                "--detect.maven.included.modules='MODULE1,MODULE2'\n" +
                "    (OPTIONAL Maven Modules Included: List of Maven modules (sub-projects) to include.)\n"
        },
    
    'NPM':
        {
            'files': ['package.json'],
            'exts': [],
            'execs': ['npm'],
            'exec_reqd': False,
            'lock_files': ['npm-shrinkwrap.json', 'package-lock.json'],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
            'cli_options':
                "--detect.npm.path=PATH_TO_NPM\n" +
                "    (OPTIONAL Path of the npm executable.)\n" +
                "--detect.npm.arguments='ARG1 ARG2'\n" +
                "    (OPTIONAL Additional arguments to add to the npm command line when running Detect against an NPM project.)\n" +
                "--detect.npm.dependency.types.excluded=<NONE, DEV, PEER>\n" +
                "    (OPTIONAL Include NPM Development Dependencies: Set this value to false if you would like to exclude your dev dependencies.)\n",
        },
    
    'NUGET':
        {
            'files': [],
            'exts': ['.sln', '.csproj', '.fsproj', '.vbproj', '.asaproj', '.dcproj', '.shproj',
            '.ccproj', '.sfproj', '.njsproj', '.vcxproj', '.vcproj', '.xproj', '.pyproj',
            '.hiveproj', '.pigproj', '.jsproj', '.usqlproj', '.deployproj', '.msbuildproj',
            '.sqlproj', '.dbproj', '.rproj'],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
            'cli_options':
                "--detect.nuget.config.path=PATH\n" + \
                "    (OPTIONAL The path to the Nuget.Config file to supply to the nuget exe)\n" + \
                "--detect.nuget.packages.repo.url=URL\n" + \
                "    (OPTIONAL Nuget Packages Repository URL (default: https://api.nuget.org/v3/index.json).)\n" + \
                "--detect.nuget.excluded.modules=PROJECT\n" + \
                "    (OPTIONAL Nuget Projects Excluded: The names of the projects in a solution to exclude.)\n" + \
                "--detect.nuget.ignore.failure=true\n" + \
                "    (OPTIONAL Ignore Nuget Failures: If true errors will be logged and then ignored.)\n" + \
                "--detect.nuget.included.modules=PROJECT\n" + \
                "    (OPTIONAL Nuget Modules Included: The names of the projects in a solution to include (overrides exclude).)\n",

        },
    
    'PACKAGIST':
        {
            'files': ['composer.json'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['composer.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.packagist.include.dev.dependencies=false\n" + \
                "    (OPTIONAL Include Packagist Development Dependencies: Set this value to false if you would like to exclude your dev requires dependencies.)\n",   
        },
    
    'PEAR':
        {
            'files': ['package.xml'],
            'exts': [],
            'execs': ['pear'],
            'exec_reqd': True,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.pear.only.required.deps=true\n" + \
               "    (OPTIONAL Include Only Required Pear Dependencies: Set to true if you would like to include only required packages.)\n",
 
        },
    
    'PIP':
        {
            'files': ['Pipfile','Pipfile.lock'],
            'exts': [],
            'execs': ['python', 'python3'],
            'exec_reqd': False,
            'lock_files': ['Pipfile.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.pip.only.project.tree=true\n" + \
                "    (OPTIONAL PIP Include Only Project Tree: By default, pipenv includes all dependencies found in the graph. Set to true to only\n" + \
                "    include dependencies found underneath the dependency that matches the provided pip project and version name.)\n" + \
                "--detect.pip.project.name=NAME\n" + \
                "    (OPTIONAL PIP Project Name: The name of your PIP project, to be used if your project's name cannot be correctly inferred from its setup.py file.)\n" + \
                "--detect.pip.project.version.name=VERSION\n" + \
                "    (OPTIONAL PIP Project Version Name: The version of your PIP project, to be used if your project's version name\n" + \
                "    cannot be correctly inferred from its setup.py file.)\n"
        },
    
    'PIP_REQTS':
        {
            'files': ['requirements.txt', 'setup.py'],
            'exts': [],
            'execs': ['pip', 'pip3'],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'LOW',
            'cli_options':
                "--detect.pip.only.project.tree=true\n" + \
                "    (OPTIONAL PIP Include Only Project Tree: By default, pipenv includes all dependencies found in the graph. Set to true to only\n" + \
                "    include dependencies found underneath the dependency that matches the provided pip project and version name.)\n" + \
                "--detect.pip.project.name=NAME\n" + \
                "    (OPTIONAL PIP Project Name: The name of your PIP project, to be used if your project's name cannot be correctly inferred from its setup.py file.)\n" + \
                "--detect.pip.project.version.name=VERSION\n" + \
                "    (OPTIONAL PIP Project Version Name: The version of your PIP project, to be used if your project's version name\n" + \
                "    cannot be correctly inferred from its setup.py file.)\n"
        },

    'PNPM':
        {
            'files': ['pnpm-lock.yaml'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['pnpm-lock.yaml'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'POETRY':
        {
            'files': ['pyproject.toml', 'Poetry.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Poetry.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
        },
    
    'RUBYGEMS':
        {
            'files': ['Gemfile.lock'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Gemfile.lock'],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.ruby.include.dev.dependencies=true\n" + \
                "    (OPTIONAL Ruby Development Dependencies: If set to true, development dependencies will be included when parsing *.gemspec files.)\n" + \
                "--detect.ruby.include.runtime.dependencies=false\n" + \
                "    (OPTIONAL Ruby Runtime Dependencies: If set to false, runtime dependencies will not be included when parsing *.gemspec files.)\n",
        },
    
    'SBT':
        {
            'files': ['build.sbt'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': [],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.sbt.report.search.depth\n" + \
                "    (OPTIONAL SBT Report Search Depth: Depth the sbt detector will use to search for report files (default 3))\n" + \
                "--detect.sbt.excluded.configurations='CONFIG'\n" + \
                "    (OPTIONAL SBT Configurations Excluded: The names of the sbt configurations to exclude.)\n" + \
                "--detect.sbt.included.configurations='CONFIG'\n" + \
                "    (OPTIONAL SBT Configurations Included: The names of the sbt configurations to include.)\n",
        },
    
    'SWIFT':
        {
            'files': ['Package.swift'],
            'exts': [],
            'execs': ['swift'],
            'exec_reqd': False,
            'lock_files': ['Package.resolved'],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
        },
    
    'XCODE':
        {
            'files': [],
            'exts': ['.xcworkspace', '.xcodeproj'],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['Package.resolved'],
            'lockfile_reqd': False,
            'accuracy': 'HIGH',
        },
    
    'YARN':
        {
            'files': ['package.json'],
            'exts': [],
            'execs': [],
            'exec_reqd': False,
            'lock_files': ['yarn.lock'],
            'lockfile_reqd': True,
            'accuracy': 'HIGH',
            'cli_options':
                "--detect.yarn.prod.only=true\n" + \
                "    (OPTIONAL Include Yarn Production Dependencies Only: Set this to true to only scan production dependencies.)\n"
        },
}

cli_msgs_dict = {
    'reqd': "--blackduck.url=https://YOURSERVER\n" + \
             "--blackduck.api.token=YOURTOKEN\n", 'proj': "--detect.project.name=PROJECT_NAME\n" + \
                                                          "--detect.project.version.name=VERSION_NAME\n" + \
                                                          "    (OPTIONAL Specify project and version names)\n",
     'scan': '', 'size': '', 'dep': '', 'lic': '', 'rep': "",
     'detect_linux': " bash <(curl -s -L https://detect.synopsys.com/detect9.sh)\n",
     'detect_linux_proxy': " (You may need to configure a proxy to download and run the Detect script as follows)\n" + \
                           " export DETECT_CURL_OPTS='--proxy http://USER:PASSWORD@PROXYHOST:PROXYPORT'\n" + \
                           " bash <(curl -s -L ${DETECT_CURL_OPTS} https://detect.synopsys.com/detect9.sh)\n" + \
                           "--blackduck.proxy.host=PROXYHOST\n" + \
                           "--blackduck.proxy.port=PROXYPORT\n" + \
                           "--blackduck.proxy.username=USERNAME\n" + \
                           "--blackduck.proxy.password=PASSWORD\n",
     'detect_win': " powershell \"[Net.ServicePointManager]::SecurityProtocol = 'tls12'; irm https://detect.synopsys.com/detect9.ps1?$(Get-Random) | iex; detect\"\n",
     'detect_win_proxy': " (You may need to configure a proxy to download and run the Detect script as follows)\n" + \
                         "    ${Env:blackduck.proxy.host} = PROXYHOST\n" + \
                         "    ${Env:blackduck.proxy.port} = PROXYPORT\n" + \
                         "    ${Env:blackduck.proxy.password} = PROXYUSER\n" + \
                         "    ${Env:blackduck.proxy.username} = PROXYPASSWORD\n" + \
                         "    powershell \"[Net.ServicePointManager]::SecurityProtocol = 'tls12'; irm https://detect.synopsys.com/detect9.ps1?$(Get-Random) | iex; detect\"\n",
     'detect': '',
     'files': ''
}

largesize = 10000000
hugesize = 100000000

notinarc = 0
inarc = 1
inarcunc = 1
inarccomp = 2

#
# Variables
max_arc_depth = 0

counts = {
    'file': [0, 0],
    'dir': [0, 0],
    'ignoredir': [0, 0],
    'arc': [0, 0],
    'bin': [0, 0],
    'jar': [0, 0],
    'src': [0, 0],
    'det': [0, 0],
    'large': [0, 0],
    'huge': [0, 0],
    'other': [0, 0],
    'lic': [0, 0],
    'pkg': [0, 0]
}

sizes = {
    'file': [0, 0, 0],
    'dir': [0, 0, 0],
    'ignoredir': [0, 0, 0],
    'arc': [0, 0, 0],
    'bin': [0, 0, 0],
    'jar': [0, 0, 0],
    'src': [0, 0, 0],
    'det': [0, 0, 0],
    'large': [0, 0, 0],
    'huge': [0, 0, 0],
    'other': [0, 0, 0],
    'pkg': [0, 0, 0]
}

file_list = {
    'src': [],
    'bin': [],
    'large': [],
    'huge': [],
    'arc': [],
    'jar': [],
    'other': [],
    'pkg': [],
    'js_single': [],
    'arcs_pm': [],
    'det': [],
}

files_dict = {
    'bin_large': {},
    'det': {},
    'large': {}
}

detectors_list = []

dir_dict = {}

recs_msgs_dict = {
    'crit': '',
    'imp': '',
    'info': ''
}

rep = ""
full_rep = ""
messages = ""
