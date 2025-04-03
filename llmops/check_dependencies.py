import pkg_resources
import re

# List of required packages with version specifications
required_packages = [
    "google-ai-generativelanguage==0.2.0",
    "google-api-core==2.11.0",
    "google-api-python-client==2.94.0",
    "google-auth==2.22.0",
    "google-auth-httplib2==0.1.0",
    "google-auth-oauthlib",
    "google-cloud-aiplatform==1.39.0",
    "google-cloud-bigquery==3.11.0",
    "google-cloud-core==2.3.2",
    "google-cloud-resource-manager==1.10.1",
    "google-cloud-storage==2.9.0",
    "google-crc32c==1.5.0",
    "google-generativeai==0.1.0",
    "google-resumable-media==2.5.0",
    "googleapis-common-protos==1.59.0",
    "kfp==2.4.0",
    "vertexai==0.0.1",
    "python-dotenv==1.0.0",
    "scikit-learn==1.2.2",
    "mplcursors==0.5.2",
    "ipympl==0.9.3",
    "tqdm==4.65.0",
    "protobuf==3.19.6",
    "ipython==8.14.0",
    "pandas==2.0.2",
    "pyarrow==12.0.1"
]

# Get installed packages
installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

print("Dependency Check Results:\n")
print("{:<40} {:<15} {:<15} {:<10}".format("Package", "Required", "Installed", "Status"))
print("-" * 80)

missing = []
version_mismatch = []
installed = []

for package_spec in required_packages:
    # Parse package name and version requirement
    if "==" in package_spec:
        package_name, required_version = package_spec.split("==")
        exact_version = True
    else:
        package_name = package_spec
        required_version = "Any"
        exact_version = False
    
    # Normalize package name to match pkg_resources format
    norm_name = re.sub(r'[-_.]+', '-', package_name).lower()
    
    # Check if package is installed
    if norm_name in installed_packages:
        installed_version = installed_packages[norm_name]
        
        # Check version if exact version is required
        if exact_version and installed_version != required_version:
            status = "Version Mismatch"
            version_mismatch.append(f"{package_name}: required {required_version}, installed {installed_version}")
        else:
            status = "Installed"
            installed.append(package_name)
    else:
        status = "Missing"
        missing.append(package_name)
        installed_version = "N/A"
    
    print("{:<40} {:<15} {:<15} {:<10}".format(
        package_name, required_version, installed_version, status))

print("\nSummary:")
print(f"Total packages checked: {len(required_packages)}")
print(f"Installed correctly: {len(installed)}")
print(f"Version mismatch: {len(version_mismatch)}")
print(f"Missing: {len(missing)}")

if missing:
    print("\nMissing Packages:")
    for pkg in missing:
        print(f"  - {pkg}")

if version_mismatch:
    print("\nVersion Mismatches:")
    for mismatch in version_mismatch:
        print(f"  - {mismatch}")

if not missing and not version_mismatch:
    print("\nAll required packages are installed with the correct versions!")
else:
    print("\nCommand to install missing or update packages:")
    install_cmd = "pip install " + " ".join([p for p in required_packages if p.split("==")[0] in missing or any(p.split("==")[0] in m for m in version_mismatch)])
    print(install_cmd)
