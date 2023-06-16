# Create a conda environment from a repo named nnpdf_branch
# Environment will be called nnpdf-branch
# Arg: path to the repo


# Check if repo path is given
[[ $# -ne 1 ]] && { echo "Usage: $0 repo_path"; exit 1; }
cd $1

source ~/.bashrc

dir_name=$(basename "$PWD")
pwd
echo "dir_name ${dir_name}"
prefix="nnpdf_"

if [[ $dir_name == $prefix* ]]; then
    # Extract the branch name
    branch=${dir_name#$prefix}
    ENV="nnpdf-${branch}"
    echo "You are about to create an environment called ${ENV}."
    echo "... and a subdirectory build inside the directory $(pwd) where it will be built."
    echo "Do you wish to continue? [y/N]"
    read response
    if [[ $response =~ ^[Yy]$ ]]; then
        # Continue with your script
        echo "Continuing with the script..."
    else
        echo "Aborting..."
        exit 1
    fi
else
    echo "Warning: The parent directory does not start with 'nnpdf_'. Please check your setup."
    exit 1
fi

setup.sh $ENV .
