#!/usr/bin/env python3

"""
Provide Statistics About Nginx Logs Stored in MongoDB
"""

from pymongo import MongoClient


def log_stats():
    """
    Provide statistics about Nginx logs stored in MongoDB
    """
    client = MongoClient('mongodb://127.0.0.1:27017')
    logs_collection = client.logs.nginx

    # Get the total number of logs
    total_logs = logs_collection.count_documents({})

    # Get the number of logs with each HTTP method
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    method_stats = {method: logs_collection.count_documents({"method": method}) for method in methods}

    # Get the number of logs with method=GET and path=/status
    status_check = logs_collection.count_documents({"method": "GET", "path": "/status"})

    # Display the results
    print(f"{total_logs} logs")
    print("Methods:")
    for method, count in method_stats.items():
        print(f"\tmethod {method}: {count}")
    print(f"{status_check} status check")

    # Get the top 10 most present IPs
    pipeline = [
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    top_ips = list(logs_collection.aggregate(pipeline))

    print("IPs:")
    for ip_data in top_ips:
        ip = ip_data["_id"]
        count = ip_data["count"]
        print(f"\t{ip}: {count}")

if __name__ == "__main__":
    log_stats()
