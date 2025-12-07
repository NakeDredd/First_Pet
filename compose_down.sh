#!/bin/bash

docker compose down && 
docker image rm first_pet-public-endpoint first_pet-date-server first_pet-timezone-converter
