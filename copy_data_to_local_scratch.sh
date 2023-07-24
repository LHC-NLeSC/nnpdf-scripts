#!/bin/bash

# Copies data to node-local scratch

ENVNAME=$1

CONDADATADIR="${HOME}/.conda/envs/${ENVNAME}/share"
tmpdir=$(mktemp -d)

echo "Copying shared data in ${CONDADATADIR} to local NVME storage ${tmpdir}..."

cp -r ${CONDADATADIR}/* ${tmpdir}/
sed -i "s|${SHAREDIR}|${tmpdir}|" ${tmpdir}/NNPDF/nnprofile.yaml
export NNPDF_PROFILE_PATH=${tmpdir}/NNPDF/nnprofile.yaml
