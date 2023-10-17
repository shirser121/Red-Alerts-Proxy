# 🚨 Red Alerts Proxy 

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Docker Supported](https://img.shields.io/badge/docker-supported-299ce8)
![License: MIT](https://img.shields.io/badge/license-MIT-blue)

A streamlined proxy service for fetching and caching red alerts, powered by Flask, Gunicorn, Celery, and Redis.

## 🚀 Features

- 📦 **Real-time Caching**: Alerts are cached in real-time using Redis for instant retrieval.
- 🔧 **Efficient Data Handling**: Leveraging the power of Flask and Celery for efficient data processing and retrieval.
- 🛠️ **Customizable Update Intervals**: Set your desired data refresh rate.
  
## 📖 Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## 🏁 Getting Started

### Prerequisites

1. Docker & Docker-compose installed
2. Python version 3.8 or higher

### Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/shirser121/red-alerts-proxy.git
    ```

2. **Build Docker Containers**
    ```bash
    cd red-alerts-proxy
    docker-compose build
    ```

3. **Run the Service**
    ```bash
    docker-compose up
    ```

### Configuration

- Set essential environment variables:
  - `API_URL`: URL for fetching alerts.
  - `UPDATE_INTERVAL`: Desired data refresh rate in seconds.

## 🔍 Usage

Simply navigate to `http://localhost:3007` and utilize the provided API endpoints.

## 🚀 Endpoints

- **Root (`/`)**: Retrieves all alerts. Supports filtering.
  - `city`: Filter by city name.
  - `since_date`: Get alerts post after specific date, in timestamp.
  - `since_id`: Get alerts post a specific ID.
  - ...

## 🤝 Contributing

Contributions are welcomed! Please read the [contributing guidelines](./CONTRIBUTING.md) for detailed steps.

## 📜 License

This project is under the [MIT License](./LICENSE).

## 👏 Credits

- **OpenAI**: For the exceptional guidance and support.
- ...

