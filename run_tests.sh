#!/bin/bash

echo "======================================="
echo "Запуск тестов микросервисов"
echo "======================================="

# Установка зависимостей для тестов
echo "1. Установка зависимостей для тестов..."
pip install -r requirements-test.txt

# Установка зависимостей для каждого микросервиса
echo "2. Установка зависимостей микросервисов..."
cd src/date-server && pip install -r requirements.txt && cd ../..
cd src/public-endpoint && pip install -r requirements.txt && cd ../..
cd src/timezone-converter && pip install -r requirements.txt && cd ../..

# Запуск тестов
echo "3. Запуск тестов..."
echo "---------------------------------------"

echo "Тестируем date-server:"
python -m pytest tests/test_date_server.py -v

echo "---------------------------------------"
echo "Тестируем public-endpoint:"
python -m pytest tests/test_public_endpoint.py -v

echo "---------------------------------------"
echo "Тестируем timezone-converter:"
python -m pytest tests/test_timezone_converter.py -v

echo "---------------------------------------"
echo "Запуск всех тестов сразу:"
python -m pytest tests/ -v

echo "======================================="
echo "Тестирование завершено!"
echo "======================================="