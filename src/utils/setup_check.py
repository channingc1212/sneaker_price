import os
import sys
import pkg_resources
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        logger.error(f"Python {required_version[0]}.{required_version[1]} or higher is required")
        return False
    return True

def check_requirements() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed."""
    requirements_path = Path(__file__).parent.parent.parent / "requirements.txt"
    missing_packages = []
    
    if not requirements_path.exists():
        logger.error("requirements.txt not found")
        return False, ["requirements.txt not found"]
    
    with open(requirements_path) as f:
        requirements = pkg_resources.parse_requirements(f)
        for requirement in requirements:
            try:
                pkg_resources.require(str(requirement))
            except pkg_resources.DistributionNotFound:
                missing_packages.append(str(requirement))
            except pkg_resources.VersionConflict:
                missing_packages.append(f"{requirement} (version conflict)")
    
    return len(missing_packages) == 0, missing_packages

def check_env_variables() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def verify_setup() -> bool:
    """Verify all requirements are met."""
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
        logger.error("Python version check failed")
    
    # Check required packages
    packages_ok, missing_packages = check_requirements()
    if not packages_ok:
        all_good = False
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
    
    # Check environment variables
    env_ok, missing_vars = check_env_variables()
    if not env_ok:
        all_good = False
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
    
    return all_good 