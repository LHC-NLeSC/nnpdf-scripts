#!/bin/bash
# This script sets up the conda environment for nnpdf.
# Args: 
# - environment name
# - path to repo


# Check if environment is given
[[ $# -ne 2 ]] && { echo "Usage: $0 envname path_to_repo"; exit 1; }

ENV=$1
BUILD_PATH=$2

echo "Creating and activating new environment $ENV..."
source ~/.bashrc
anaconda  # a script defined in the bashrc that loads the anaconda module
conda create -n "$ENV" python=3.10 --yes
conda activate "$ENV"

echo "Installing deps of nnpdf..."
mamba install --yes --only-deps nnpdf

echo "Installing swig, pkg-config, make"
mamba install --yes swig pkg-config make

echo "Building nnpdf..."
cd $BUILD_PATH
build_dir="build_$ENV"  # putting the env name in the builddir makes it easy to experiment
rm -rf $build_dir
mkdir $build_dir
cd $build_dir

cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
make
make install
