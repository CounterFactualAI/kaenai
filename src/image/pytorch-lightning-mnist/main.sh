#!/bin/bash
torchrun \
	--nnodes ${KAEN_WORLD_SIZE:-1} \
	--nproc_per_node ${KAEN_NPROC_PER_NODE:-1} \
	--rdzv_id ${KAEN_JOB:-0} \
	--rdzv_backend c10d \
  --rdzv_endpoint=${KAEN_JOB_MANAGER_HOST:-localhost}:${KAEN_JOB_MANAGER_PORT:-23400} \
	$@
