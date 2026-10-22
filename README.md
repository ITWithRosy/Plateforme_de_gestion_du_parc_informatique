
# IT Infrastructure Management & Monitoring Platform

## Overview

This project is a web-based platform developed to centralize the management, monitoring and administration of an IT infrastructure.

The platform provides a unified interface for managing IT equipment, monitoring infrastructure status, viewing alerts, tracking administrative actions and carrying out selected administrative tasks.

The solution was developed in a virtualized environment and integrates data from infrastructure monitoring and network services through their APIs.

---

## Objectives

The main objectives of the project are to:

- Centralize IT infrastructure information in a single web interface
- Facilitate the monitoring of infrastructure health and availability
- Manage and track IT equipment
- Provide a centralized view of monitoring alerts
- Improve traceability of administrative operations
- Automate selected recurring administrative tasks
- Secure access to the platform through authentication and role-based access control

---

## Main Features

### Monitoring Dashboard

The dashboard provides a centralized overview of the infrastructure, including:

- Number of monitored equipment
- Equipment availability
- Host status
- CPU and RAM resource usage
- Monitoring alerts
- Network and firewall information

Monitoring data is retrieved from Zabbix and displayed through the web interface.

### Equipment Management

The equipment management module allows administrators to:

- View registered equipment
- Add equipment
- Update equipment information
- Delete equipment
- View equipment status
- Consult resource usage information

Each equipment record can include information such as its IP address, type and operational status.

### User Management

The platform includes an authentication system with role-based access control.

Implemented mechanisms include:

- User authentication
- User roles
- Protected routes
- Access control decorators
- Role-based redirection

Different functionalities are therefore restricted according to the authenticated user's permissions.

### Alert Monitoring

The platform centralizes monitoring alerts retrieved from the infrastructure monitoring system.

Alerts are displayed according to their severity, allowing administrators to quickly identify relevant infrastructure events.

### Task Automation

The platform includes functionality for automating selected recurring administrative tasks.

The objective is to reduce repetitive manual operations and facilitate day-to-day infrastructure administration.

### Audit Journal

Administrative actions performed on the platform are recorded in an audit journal.

Each log contains information such as:

- User
- Action performed
- Date and time
- IP address
- Result
- Description

The audit journal also provides filtering capabilities and CSV export.

Access to the audit journal is restricted to authorized administrators.

### Reports & Statistics

The reports section provides summarized infrastructure statistics, including:

- Equipment distribution by type
- Alert distribution by severity
- Infrastructure indicators

The displayed statistics can be printed or exported to PDF using the browser's print functionality.

The application communicates with PostgreSQL for persistent data storage and with infrastructure services through APIs.

###  Technologies
 
 ### Backend
 - Python
 - Flask
 - SQLAlchemy / Flask-SQLAlchemy

 ### Database
 - PostgreSQL

 ### Infrastructure & Monitoring
 - Zabbix
 - pfSense
 - VMware Workstation
 - Ubuntu Server
 - Windows 10
 - Debian

 ### Frontend
 - HTML
 - CSS
 - Bootstrap
 - JavaScript
 - Chart.js

 ### Development Environment
 - Visual Studio Code
 - Git / GitHub

###  API Integration

 ### Zabbix API

The platform communicates with Zabbix to retrieve infrastructure monitoring information.
The collected information includes:

 - Host status
 - Monitoring alerts
 - Resource usage
 - Equipment availability

This data is then processed and displayed through the platform's dashboard.

 ### pfSense

pfSense is used within the virtualized infrastructure as a firewall and network control point.

The project also includes work toward integrating network information from pfSense through its API.

The intended data includes:

 - Network interface status
 - Traffic statistics

Further integration remains part of the project's future development.

###   Security

Security was considered at the application level through several mechanisms:

 ### Authentication

Users must authenticate before accessing the platform.

### Role-Based Access Control

Access to sensitive functionality is restricted according to user roles.

### Audit Logging

Administrative actions are recorded to provide traceability and facilitate auditing.

### Environment Variables

Sensitive configuration values such as credentials, secret keys and API tokens are stored through environment variables rather than directly in the source code.

Sensitive credentials and environment configuration files are intentionally excluded from this repository.

###  Testing

The main functionalities of the platform were tested during development.
Tests covered areas such as:

 - User authentication
 - Role-based access control
 - Equipment management
 - Monitoring data retrieval
 - Alert display
 - Audit logging
 - CSV export
 - Statistics and report display

The tests confirmed the operation of the main implemented functionalities.

###  Current Limitations

The current version has several limitations:
 - pfSense integration is not yet fully implemented.
 - Advanced centralized security event management is not currently integrated.
 - Multi-factor authentication is not implemented.

###  Future Improvements

Possible future developments include:

 - Complete pfSense API integration
 - Integration with a centralized security monitoring solution such as Wazuh
 - Multi-factor authentication (MFA)
 - Stronger protection of communications
 - Automated PDF report generation
 - Extended infrastructure automation
 - Additional monitoring and security indicators

###  Project Context

This project was developed as part of an academic internship in the field of computer networks and cybersecurity.

The implementation was carried out in a virtualized environment designed to reproduce a representative IT infrastructure, including servers, client machines, network services and monitoring components.

The project provided practical experience in:

 - Web application development
 - System and network administration
 - Infrastructure monitoring
 - API integration
 - Database management
 - Authentication and access control
 - Audit logging
 - Virtualized infrastructure deployment

###  Author

Rosy Ndongo Ekoum

Computer Science Student
Networks & Cybersecurity

