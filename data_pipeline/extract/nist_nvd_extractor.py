"""
NIST NVD CVE Data Extractor
============================

Extracts vulnerability data from NIST National Vulnerability Database API.
Saves to CSV for loading into Snowflake data warehouse.

API Documentation: https://nvd.nist.gov/developers/vulnerabilities

Author: Deepthi Desharaju
Date: February 2026
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NISTNVDExtractor:
    """
    Extracts CVE vulnerability data from NIST NVD API.
    """
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    RESULTS_PER_PAGE = 2000  # API max
    RATE_LIMIT_DELAY = 6  # seconds between requests (public API rate limit)
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize extractor.
        
        Args:
            api_key: Optional NIST API key for higher rate limits
        """
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'apiKey': api_key})
            self.RATE_LIMIT_DELAY = 0.6  # With API key, rate limit is higher
    
    def extract_cve_data(
        self, 
        start_date: str,
        end_date: str,
        output_dir: str = "data/raw"
    ) -> pd.DataFrame:
        """
        Extract CVE data for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            output_dir: Directory to save extracted data
            
        Returns:
            DataFrame containing CVE records
        """
        logger.info(f"Extracting CVEs from {start_date} to {end_date}")
        
        all_cves = []
        start_index = 0
        total_results = None
        
        while True:
            # Build API request URL
            params = {
                'pubStartDate': f"{start_date}T00:00:00.000",
                'pubEndDate': f"{end_date}T23:59:59.999",
                'resultsPerPage': self.RESULTS_PER_PAGE,
                'startIndex': start_index
            }
            
            try:
                logger.info(f"Fetching records {start_index} to {start_index + self.RESULTS_PER_PAGE}")
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Get total results on first request
                if total_results is None:
                    total_results = data.get('totalResults', 0)
                    logger.info(f"Total CVEs to fetch: {total_results}")
                
                # Extract vulnerabilities from response
                vulnerabilities = data.get('vulnerabilities', [])
                
                if not vulnerabilities:
                    logger.info("No more results. Extraction complete.")
                    break
                
                # Parse each CVE
                for vuln in vulnerabilities:
                    cve_data = self._parse_cve(vuln)
                    all_cves.append(cve_data)
                
                # Move to next page
                start_index += len(vulnerabilities)
                
                # Check if we've fetched all results
                if start_index >= total_results:
                    logger.info("All CVEs extracted successfully.")
                    break
                
                # Rate limiting
                time.sleep(self.RATE_LIMIT_DELAY)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                break
        
        # Convert to DataFrame
        df = pd.DataFrame(all_cves)
        logger.info(f"Extracted {len(df)} CVE records")
        
        # Save to CSV
        self._save_to_csv(df, output_dir, start_date, end_date)
        
        return df
    
    def _parse_cve(self, vuln_data: Dict) -> Dict:
        """
        Parse a single CVE vulnerability record.
        
        Args:
            vuln_data: Raw CVE data from API
            
        Returns:
            Parsed CVE dictionary
        """
        cve = vuln_data.get('cve', {})
        cve_id = cve.get('id', '')
        
        # Basic metadata
        published = cve.get('published', '')
        modified = cve.get('lastModified', '')
        vuln_status = cve.get('vulnStatus', '')
        
        # Description (take first English description)
        descriptions = cve.get('descriptions', [])
        description = next(
            (d['value'] for d in descriptions if d.get('lang') == 'en'),
            ''
        )
        
        # CVSS v3.1 metrics (primary scoring system)
        metrics = cve.get('metrics', {})
        cvss_v3 = metrics.get('cvssMetricV31', [])
        
        cvss_score = None
        cvss_severity = None
        attack_vector = None
        attack_complexity = None
        privileges_required = None
        user_interaction = None
        exploitability_score = None
        impact_score = None
        
        if cvss_v3:
            cvss_data = cvss_v3[0].get('cvssData', {})
            cvss_score = cvss_data.get('baseScore')
            cvss_severity = cvss_data.get('baseSeverity')
            attack_vector = cvss_data.get('attackVector')
            attack_complexity = cvss_data.get('attackComplexity')
            privileges_required = cvss_data.get('privilegesRequired')
            user_interaction = cvss_data.get('userInteraction')
            
            exploitability_score = cvss_v3[0].get('exploitabilityScore')
            impact_score = cvss_v3[0].get('impactScore')
        
        # CWE (Common Weakness Enumeration)
        weaknesses = cve.get('weaknesses', [])
        cwe_ids = []
        for weakness in weaknesses:
            descriptions = weakness.get('description', [])
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    cwe_ids.append(desc.get('value', ''))
        cwe_id = ', '.join(cwe_ids) if cwe_ids else None
        
        # References
        references = cve.get('references', [])
        reference_count = len(references)
        
        # Extract vendor and product info
        configurations = cve.get('configurations', [])
        products = []
        vendors = []
        
        for config in configurations:
            nodes = config.get('nodes', [])
            for node in nodes:
                cpe_matches = node.get('cpeMatch', [])
                for cpe in cpe_matches:
                    cpe_uri = cpe.get('criteria', '')
                    # CPE format: cpe:2.3:a:vendor:product:version...
                    parts = cpe_uri.split(':')
                    if len(parts) >= 5:
                        vendors.append(parts[3])
                        products.append(parts[4])
        
        vendor = vendors[0] if vendors else None
        product = ', '.join(set(products[:3])) if products else None  # Top 3 unique products
        
        return {
            'cve_id': cve_id,
            'published_date': published,
            'modified_date': modified,
            'vuln_status': vuln_status,
            'description': description[:500] if description else None,  # Truncate long descriptions
            'cvss_v3_score': cvss_score,
            'cvss_v3_severity': cvss_severity,
            'attack_vector': attack_vector,
            'attack_complexity': attack_complexity,
            'privileges_required': privileges_required,
            'user_interaction': user_interaction,
            'exploitability_score': exploitability_score,
            'impact_score': impact_score,
            'cwe_id': cwe_id,
            'vendor': vendor,
            'product': product,
            'reference_count': reference_count,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _save_to_csv(
        self, 
        df: pd.DataFrame, 
        output_dir: str,
        start_date: str,
        end_date: str
    ):
        """Save DataFrame to CSV file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"cve_data_{start_date}_to_{end_date}.csv"
        filepath = output_path / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")


def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(
        description='Extract CVE data from NIST NVD API'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days to look back from today (default: 365)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date in YYYY-MM-DD format (overrides --days)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date in YYYY-MM-DD format (default: today)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='NIST API key for higher rate limits (optional)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for CSV files (default: data/raw)'
    )
    
    args = parser.parse_args()
    
    # Calculate date range
    if args.start_date:
        start_date = args.start_date
    else:
        start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
    
    end_date = args.end_date
    
    # Initialize extractor
    extractor = NISTNVDExtractor(api_key=args.api_key)
    
    # Extract data
    df = extractor.extract_cve_data(
        start_date=start_date,
        end_date=end_date,
        output_dir=args.output_dir
    )
    
    # Display summary statistics
    logger.info("\n=== Extraction Summary ===")
    logger.info(f"Total CVEs: {len(df)}")
    if 'cvss_v3_severity' in df.columns:
        logger.info("\nSeverity Distribution:")
        logger.info(df['cvss_v3_severity'].value_counts())
    logger.info(f"\nDate Range: {start_date} to {end_date}")


if __name__ == "__main__":
    main()
