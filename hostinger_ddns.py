#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hostinger_api
from hostinger_api.rest import ApiException
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# --- Load Configuration from .env ---
# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables with defaults
API_TOKEN = os.getenv("API_TOKEN", "")
DOMAIN = os.getenv("DOMAIN", "example.com")
SUBDOMAIN = os.getenv("SUBDOMAIN", "vpn")
TTL = int(os.getenv("TTL", "60"))
LOG_FILE = os.getenv("LOG_FILE", "/tmp/hostinger-ddns-python.log")
LAST_IP_FILE = os.getenv("LAST_IP_FILE", "/tmp/hostinger-ddns-python-last-ip.txt")
# --- End Configuration ---

# --- Logging Function ---
def log_message(message):
    """Appends a timestamped message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    try:
        # Use 'a' mode to append. Create file if it doesn't exist.
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        # Fallback to printing if logging fails
        print(f"Error writing to log file {LOG_FILE}: {e}")
        print(log_entry)

# --- Ensure log file exists and has permissions ---
try:
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
         os.makedirs(log_dir) # Create directory if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("") # Create empty file
    # Attempt to make it writable by owner (best effort)
    # os.chmod(LOG_FILE, 0o644)
except Exception as e:
    print(f"Warning: Could not ensure log file {LOG_FILE} exists/permissions: {e}")


# --- Function to get current public IP ---
def get_current_ip():
    """Fetches the current public IPv4 address from ifconfig.me."""
    try:
        response = requests.get('https://ifconfig.me', timeout=15) # Increased timeout slightly
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        ip = response.text.strip()
        # Basic IPv4 validation
        if ip and len(ip.split('.')) == 4:
            return ip
        else:
             log_message(f"ERROR: Invalid IP format received from ifconfig.me: '{ip}'")
             return None
    except requests.RequestException as e:
        log_message(f"ERROR: Could not get current IP from ifconfig.me: {e}")
        return None
    except Exception as e:
        log_message(f"ERROR: Unexpected error getting current IP: {e}")
        return None

# --- Function to get last known IP ---
def get_last_ip():
    """Reads the last known IP address from the temporary file."""
    if os.path.exists(LAST_IP_FILE):
        try:
            with open(LAST_IP_FILE, "r") as f:
                return f.read().strip()
        except Exception as e:
            log_message(f"WARN: Could not read last IP file {LAST_IP_FILE}: {e}")
    return None

# --- Function to save the last known IP ---
def save_last_ip(ip):
    """Saves the given IP address to the temporary file."""
    try:
        with open(LAST_IP_FILE, "w") as f:
            f.write(ip)
    except Exception as e:
        log_message(f"ERROR: Could not write to last IP file {LAST_IP_FILE}: {e}")

# --- Function to update DNS record using Hostinger SDK (v1 endpoint logic) ---
def update_dns_record(target_ip):
    """
    Updates the specified DNS A record using the Hostinger API v1 endpoint.
    
    Uses the update_dns_records_v1 endpoint which:
    - Takes domain name and a DNSV1ZoneUpdateRequest object
    - Returns CommonSuccessEmptyResource on success (HTTP 200)
    - With overwrite=True, replaces existing A records matching name and type
    """
    # Validate API token at runtime
    if not API_TOKEN or len(API_TOKEN) < 20:
        log_message("ERROR: API_TOKEN is not set or invalid. Update hostinger_ddns.py with your real token.")
        return False
    
    try:
        # Configure API client with the token
        configuration = hostinger_api.Configuration(access_token=API_TOKEN)

        # Use API client context manager
        with hostinger_api.ApiClient(configuration) as api_client:
            # Create an instance of the DNS Zone API class
            api_instance = hostinger_api.DNSZoneApi(api_client)

            # Build the request using the correct model structure from the API docs:
            # DNSV1ZoneUpdateRequest(overwrite: bool, zone: List[DNSV1ZoneUpdateRequestZoneInner])
            # DNSV1ZoneUpdateRequestZoneInner(name: str, type: str, records: List[...RecordsInner], ttl: Optional[int])
            # ...RecordsInner(content: str)
            
            try:
                # Create the record content (requires 'content' field)
                record = hostinger_api.models.DNSV1ZoneUpdateRequestZoneInnerRecordsInner(
                    content=target_ip
                )

                # Create the zone entry (requires 'name', 'type', 'records'; 'ttl' is optional)
                zone_entry = hostinger_api.models.DNSV1ZoneUpdateRequestZoneInner(
                    name=SUBDOMAIN,
                    type="A",
                    ttl=TTL,
                    records=[record]
                )

                # Create the update request (requires 'zone'; 'overwrite' defaults to True)
                update_request = hostinger_api.models.DNSV1ZoneUpdateRequest(
                    overwrite=True,  # Replace existing A records for this name
                    zone=[zone_entry]
                )

            except Exception as e:
                log_message(f"ERROR: Failed to construct DNS update request: {e}")
                return False

            try:
                # Make the API call
                log_message(f"ACTION: Sending update request to Hostinger API for {SUBDOMAIN}.{DOMAIN} -> {target_ip}")
                api_response = api_instance.update_dns_records_v1(
                    domain=DOMAIN,
                    dnsv1_zone_update_request=update_request
                )

                # Success: check response type
                if isinstance(api_response, hostinger_api.CommonSuccessEmptyResource):
                    log_message(f"SUCCESS: Hostinger API accepted update for {SUBDOMAIN}.{DOMAIN} to {target_ip}")
                    return True
                else:
                    log_message(f"WARN: Unexpected response type: {type(api_response)}, Response: {api_response}")
                    # If we got here without exception, treat as success
                    return True

            except ApiException as e:
                log_message(f"ERROR: Hostinger API returned error {e.status}: {e.body}")
                if e.status == 401 or e.status == 403:
                    log_message("ERROR: Authentication failed (401/403). Verify API_TOKEN is correct.")
                    # Clear the cached IP so we retry on next run
                    if os.path.exists(LAST_IP_FILE):
                        try:
                            os.remove(LAST_IP_FILE)
                        except:
                            pass
                elif e.status == 422:
                    log_message(f"ERROR: Validation error (422). Check your subdomain/domain names and record structure.")
                elif e.status == 500:
                    log_message(f"ERROR: Server error (500) from Hostinger API.")
                return False
            except Exception as e:
                log_message(f"ERROR: Unexpected error during API call: {e}")
                import traceback
                log_message(f"TRACEBACK: {traceback.format_exc()}")
                return False

    except Exception as e:
        log_message(f"ERROR: Unexpected error in update_dns_record: {e}")
        return False

# === Main Script Logic ===
if __name__ == "__main__":
    log_message("INFO: Script started.")
    current_ip = get_current_ip()

    if not current_ip:
        log_message("ERROR: Exiting script because current IP could not be determined.")
        exit(1)

    last_ip = get_last_ip()

    if current_ip == last_ip:
        # log_message(f"INFO: Current IP ({current_ip}) matches last known IP. No update needed.") # Keep log clean
        log_message("INFO: Script finished. No IP change detected.")
        exit(0)
    else:
        log_message(f"INFO: IP change detected. Current IP: {current_ip}, Last IP: {last_ip if last_ip else 'None'}.")
        if update_dns_record(current_ip):
            save_last_ip(current_ip) # Save the new IP only on successful update confirmation
            log_message("INFO: Script finished. Update successful.")
            exit(0)
        else:
            log_message("ERROR: Script finished. Update failed.")
            # Do not save the IP if the update failed, retry next time
            exit(1)