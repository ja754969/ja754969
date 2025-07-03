#!/usr/bin/env python3
"""
Personal Dashboard Automation Script
Updates README.md with data from ResearchGate, LinkedIn, and Google Scholar
"""

import requests
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import time
import yaml

class ProfileScraper:
    """Base class for profile scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

class ResearchGateProfile(ProfileScraper):
    """Scrape ResearchGate profile data"""
    
    def __init__(self, profile_url: str):
        super().__init__()
        self.profile_url = profile_url
        
    def get_profile_data(self) -> Dict:
        """Extract profile data from ResearchGate"""
        try:
            response = self.session.get(self.profile_url)
            response.raise_for_status()
            
            # Extract basic information
            data = {
                'name': self._extract_name(response.text),
                'institution': self._extract_institution(response.text),
                'publications': self._extract_publications(response.text),
                'citations': self._extract_citations(response.text),
                'research_interests': self._extract_research_interests(response.text),
                'h_index': self._extract_h_index(response.text)
            }
            
            return data
            
        except Exception as e:
            print(f"Error scraping ResearchGate: {e}")
            return {}
    
    def _extract_name(self, html: str) -> str:
        """Extract name from HTML"""
        match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        return match.group(1).strip() if match else ""
    
    def _extract_institution(self, html: str) -> str:
        """Extract institution from HTML"""
        match = re.search(r'institution[^>]*>([^<]+)</[^>]*>', html, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_publications(self, html: str) -> int:
        """Extract publication count"""
        match = re.search(r'(\d+)\s*Publications?', html, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _extract_citations(self, html: str) -> int:
        """Extract citation count"""
        match = re.search(r'(\d+)\s*Citations?', html, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _extract_research_interests(self, html: str) -> List[str]:
        """Extract research interests"""
        # This would need to be customized based on ResearchGate's HTML structure
        return []
    
    def _extract_h_index(self, html: str) -> int:
        """Extract h-index"""
        match = re.search(r'h-index[^>]*>(\d+)', html, re.IGNORECASE)
        return int(match.group(1)) if match else 0

class GoogleScholarProfile(ProfileScraper):
    """Scrape Google Scholar profile data"""
    
    def __init__(self, profile_url: str):
        super().__init__()
        self.profile_url = profile_url
        
    def get_profile_data(self) -> Dict:
        """Extract profile data from Google Scholar"""
        try:
            response = self.session.get(self.profile_url)
            response.raise_for_status()
            
            data = {
                'name': self._extract_name(response.text),
                'citations': self._extract_citations(response.text),
                'h_index': self._extract_h_index(response.text),
                'i10_index': self._extract_i10_index(response.text),
                'publications': self._extract_publications(response.text)
            }
            
            return data
            
        except Exception as e:
            print(f"Error scraping Google Scholar: {e}")
            return {}
    
    def _extract_name(self, html: str) -> str:
        """Extract name from HTML"""
        match = re.search(r'<div[^>]*id="gsc_prf_in"[^>]*>([^<]+)</div>', html)
        return match.group(1).strip() if match else ""
    
    def _extract_citations(self, html: str) -> int:
        """Extract total citations"""
        match = re.search(r'<td[^>]*class="gsc_rsb_std"[^>]*>(\d+)</td>', html)
        return int(match.group(1)) if match else 0
    
    def _extract_h_index(self, html: str) -> int:
        """Extract h-index"""
        matches = re.findall(r'<td[^>]*class="gsc_rsb_std"[^>]*>(\d+)</td>', html)
        return int(matches[1]) if len(matches) > 1 else 0
    
    def _extract_i10_index(self, html: str) -> int:
        """Extract i10-index"""
        matches = re.findall(r'<td[^>]*class="gsc_rsb_std"[^>]*>(\d+)</td>', html)
        return int(matches[2]) if len(matches) > 2 else 0
    
    def _extract_publications(self, html: str) -> List[Dict]:
        """Extract publication list"""
        # This would extract individual publications
        return []

class LinkedInProfile(ProfileScraper):
    """LinkedIn profile scraper (limited due to restrictions)"""
    
    def __init__(self, profile_url: str):
        super().__init__()
        self.profile_url = profile_url
        
    def get_profile_data(self) -> Dict:
        """Extract available LinkedIn data"""
        # LinkedIn heavily restricts scraping
        # You would need to use LinkedIn API or manual updates
        return {
            'current_position': '',
            'education': '',
            'experience': []
        }

class DashboardUpdater:
    """Main class to update the dashboard"""
    
    def __init__(self, config_file: str = 'dashboard_config.yaml'):
        self.config = self._load_config(config_file)
        self.readme_path = self.config.get('readme_path', 'README.md')
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._create_default_config(config_file)
    
    def _create_default_config(self, config_file: str) -> Dict:
        """Create default configuration file"""
        default_config = {
            'profiles': {
                'researchgate': 'https://www.researchgate.net/profile/Yu-Hao-Tseng',
                'linkedin': 'https://www.linkedin.com/in/yu-hao-tseng-70316221b/',
                'google_scholar': 'https://scholar.google.com/citations?user=_zozF1AAAAAJ'
            },
            'readme_path': 'README.md',
            'update_frequency': 'daily',
            'sections': {
                'about': True,
                'publications': True,
                'citations': True,
                'research_interests': True,
                'education': True,
                'experience': True
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def collect_data(self) -> Dict:
        """Collect data from all profiles"""
        data = {}
        
        # ResearchGate
        if 'researchgate' in self.config['profiles']:
            rg_scraper = ResearchGateProfile(self.config['profiles']['researchgate'])
            data['researchgate'] = rg_scraper.get_profile_data()
            time.sleep(2)  # Be respectful with requests
        
        # Google Scholar
        if 'google_scholar' in self.config['profiles']:
            gs_scraper = GoogleScholarProfile(self.config['profiles']['google_scholar'])
            data['google_scholar'] = gs_scraper.get_profile_data()
            time.sleep(2)
        
        # LinkedIn (limited)
        if 'linkedin' in self.config['profiles']:
            li_scraper = LinkedInProfile(self.config['profiles']['linkedin'])
            data['linkedin'] = li_scraper.get_profile_data()
        
        return data
    
    def generate_readme(self, data: Dict) -> str:
        """Generate README.md content"""
        readme_content = f"""# Yu-Hao Tseng

## About Me
I'm a researcher at National Taiwan Ocean University, specializing in oceanography and marine sciences.

## 📊 Research Metrics
- **Publications**: {data.get('researchgate', {}).get('publications', 'N/A')}
- **Citations**: {data.get('google_scholar', {}).get('citations', 'N/A')}
- **H-index**: {data.get('google_scholar', {}).get('h_index', 'N/A')}
- **i10-index**: {data.get('google_scholar', {}).get('i10_index', 'N/A')}

## 🔬 Research Interests
- Ocean Current Analysis
- Marine Dynamics
- Geographic Information Systems (GIS)
- Data Visualization

## 📚 Education
- **National Taiwan Ocean University**
  - Department of Marine Environmental Informatics

## 🔗 Links
- [ResearchGate](https://www.researchgate.net/profile/Yu-Hao-Tseng)
- [Google Scholar](https://scholar.google.com/citations?user=_zozF1AAAAAJ)
- [LinkedIn](https://www.linkedin.com/in/yu-hao-tseng-70316221b/)

## 💻 Current Projects
- Ocean Current Observation and Analysis
- GMT (Generic Mapping Tools) Applications
- MATLAB Ocean Dynamics Modeling
- OpenDrift Trajectory Modeling

## 📈 Repository Statistics
![GitHub Stats](https://github-readme-stats.vercel.app/api?username=ja754969&show_icons=true&theme=radical)

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return readme_content
    
    def update_readme(self, content: str):
        """Update README.md file"""
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"README.md updated successfully at {datetime.now()}")
    
    def run_update(self):
        """Run the complete update process"""
        print("Starting dashboard update...")
        
        # Collect data
        data = self.collect_data()
        
        # Generate README
        readme_content = self.generate_readme(data)
        
        # Update file
        self.update_readme(readme_content)
        
        print("Dashboard update completed!")

def main():
    """Main function"""
    updater = DashboardUpdater()
    updater.run_update()

if __name__ == "__main__":
    main()
