#!/bin/bash
helm uninstall gitlab -n gitlab
kubectl delete pvc -n gitlab data-gitlab-postgresql-0