"""
Temporal Analysis Tools for GameCock AI
Specialized tools for analyzing how management views and risk factors change over time.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from database import SessionLocal, Sec10KDocument, Sec8KItem, Sec10KSubmission, Sec8KSubmission

logger = logging.getLogger(__name__)

class TemporalAnalysisEngine:
    """Engine for analyzing how SEC filing content changes over time."""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session if db_session else SessionLocal()
    
    def analyze_risk_evolution(self, company_cik: str, years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyze how risk factors have evolved over time for a company.
        
        Args:
            company_cik: Company's CIK identifier
            years: List of years to analyze (default: last 5 years)
        
        Returns:
            Dictionary with risk evolution analysis
        """
        try:
            if not years:
                current_year = datetime.now().year
                years = list(range(current_year - 4, current_year + 1))
            
            # Get all risk factor sections for the company
            risk_sections = self.db.query(Sec10KDocument).join(
                Sec10KSubmission, Sec10KDocument.accession_number == Sec10KSubmission.accession_number
            ).filter(
                and_(
                    Sec10KSubmission.cik == company_cik,
                    Sec10KDocument.section == 'risk_factors',
                    Sec10KSubmission.filing_date >= datetime(years[0], 1, 1),
                    Sec10KSubmission.filing_date <= datetime(years[-1], 12, 31)
                )
            ).order_by(Sec10KSubmission.filing_date.asc()).all()
            
            if not risk_sections:
                return {"error": f"No risk factor data found for CIK {company_cik}"}
            
            # Analyze risk content by year
            risk_analysis = {}
            for section in risk_sections:
                filing_date = self.db.query(Sec10KSubmission.filing_date).filter(
                    Sec10KSubmission.accession_number == section.accession_number
                ).scalar()
                
                year = filing_date.year
                if year not in risk_analysis:
                    risk_analysis[year] = {
                        'filing_count': 0,
                        'total_words': 0,
                        'content_samples': [],
                        'filing_dates': []
                    }
                
                risk_analysis[year]['filing_count'] += 1
                risk_analysis[year]['total_words'] += section.word_count or 0
                risk_analysis[year]['content_samples'].append(section.content[:500] + "..." if len(section.content) > 500 else section.content)
                risk_analysis[year]['filing_dates'].append(filing_date.strftime('%Y-%m-%d'))
            
            return {
                'company_cik': company_cik,
                'analysis_period': f"{years[0]}-{years[-1]}",
                'total_filings': len(risk_sections),
                'yearly_breakdown': risk_analysis,
                'summary': self._generate_risk_evolution_summary(risk_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk evolution: {e}")
            return {"error": str(e)}
    
    def analyze_management_view_evolution(self, company_cik: str, years: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Analyze how management's discussion and analysis has evolved over time.
        
        Args:
            company_cik: Company's CIK identifier
            years: List of years to analyze (default: last 5 years)
        
        Returns:
            Dictionary with MD&A evolution analysis
        """
        try:
            if not years:
                current_year = datetime.now().year
                years = list(range(current_year - 4, current_year + 1))
            
            # Get all MD&A sections for the company
            mdna_sections = self.db.query(Sec10KDocument).join(
                Sec10KSubmission, Sec10KDocument.accession_number == Sec10KSubmission.accession_number
            ).filter(
                and_(
                    Sec10KSubmission.cik == company_cik,
                    Sec10KDocument.section == 'mdna',
                    Sec10KSubmission.filing_date >= datetime(years[0], 1, 1),
                    Sec10KSubmission.filing_date <= datetime(years[-1], 12, 31)
                )
            ).order_by(Sec10KSubmission.filing_date.asc()).all()
            
            if not mdna_sections:
                return {"error": f"No MD&A data found for CIK {company_cik}"}
            
            # Analyze MD&A content by year
            mdna_analysis = {}
            for section in mdna_sections:
                filing_date = self.db.query(Sec10KSubmission.filing_date).filter(
                    Sec10KSubmission.accession_number == section.accession_number
                ).scalar()
                
                year = filing_date.year
                if year not in mdna_analysis:
                    mdna_analysis[year] = {
                        'filing_count': 0,
                        'total_words': 0,
                        'content_samples': [],
                        'filing_dates': []
                    }
                
                mdna_analysis[year]['filing_count'] += 1
                mdna_analysis[year]['total_words'] += section.word_count or 0
                mdna_analysis[year]['content_samples'].append(section.content[:500] + "..." if len(section.content) > 500 else section.content)
                mdna_analysis[year]['filing_dates'].append(filing_date.strftime('%Y-%m-%d'))
            
            return {
                'company_cik': company_cik,
                'analysis_period': f"{years[0]}-{years[-1]}",
                'total_filings': len(mdna_sections),
                'yearly_breakdown': mdna_analysis,
                'summary': self._generate_mdna_evolution_summary(mdna_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing management view evolution: {e}")
            return {"error": str(e)}
    
    def compare_risk_factors_across_companies(self, company_ciks: List[str], year: int) -> Dict[str, Any]:
        """
        Compare risk factors across multiple companies for a specific year.
        
        Args:
            company_ciks: List of company CIK identifiers
            year: Year to compare
        
        Returns:
            Dictionary with comparative risk analysis
        """
        try:
            comparison_data = {}
            
            for cik in company_ciks:
                # Get risk factors for this company in this year
                risk_sections = self.db.query(Sec10KDocument).join(
                    Sec10KSubmission, Sec10KDocument.accession_number == Sec10KSubmission.accession_number
                ).filter(
                    and_(
                        Sec10KSubmission.cik == cik,
                        Sec10KDocument.section == 'risk_factors',
                        Sec10KSubmission.filing_date >= datetime(year, 1, 1),
                        Sec10KSubmission.filing_date <= datetime(year, 12, 31)
                    )
                ).all()
                
                if risk_sections:
                    comparison_data[cik] = {
                        'filing_count': len(risk_sections),
                        'total_words': sum(section.word_count or 0 for section in risk_sections),
                        'content_samples': [section.content[:300] + "..." if len(section.content) > 300 else section.content for section in risk_sections]
                    }
                else:
                    comparison_data[cik] = {
                        'filing_count': 0,
                        'total_words': 0,
                        'content_samples': []
                    }
            
            return {
                'comparison_year': year,
                'companies_analyzed': len(company_ciks),
                'comparison_data': comparison_data,
                'summary': self._generate_comparative_risk_summary(comparison_data)
            }
            
        except Exception as e:
            logger.error(f"Error comparing risk factors: {e}")
            return {"error": str(e)}
    
    def analyze_8k_event_patterns(self, company_cik: str, months: int = 12) -> Dict[str, Any]:
        """
        Analyze patterns in 8-K filings (events) for a company.
        
        Args:
            company_cik: Company's CIK identifier
            months: Number of months to look back (default: 12)
        
        Returns:
            Dictionary with 8-K event pattern analysis
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            # Get all 8-K items for the company
            items = self.db.query(Sec8KItem).join(
                Sec8KSubmission, Sec8KItem.accession_number == Sec8KSubmission.accession_number
            ).filter(
                and_(
                    Sec8KSubmission.cik == company_cik,
                    Sec8KSubmission.filing_date >= cutoff_date
                )
            ).order_by(Sec8KSubmission.filing_date.desc()).all()
            
            if not items:
                return {"error": f"No 8-K data found for CIK {company_cik} in the last {months} months"}
            
            # Analyze by item type
            item_analysis = {}
            for item in items:
                item_type = item.item_number
                if item_type not in item_analysis:
                    item_analysis[item_type] = {
                        'count': 0,
                        'title': item.item_title,
                        'recent_examples': []
                    }
                
                item_analysis[item_type]['count'] += 1
                if len(item_analysis[item_type]['recent_examples']) < 3:
                    item_analysis[item_type]['recent_examples'].append(item.content[:200] + "..." if len(item.content) > 200 else item.content)
            
            return {
                'company_cik': company_cik,
                'analysis_period_months': months,
                'total_events': len(items),
                'item_breakdown': item_analysis,
                'summary': self._generate_8k_pattern_summary(item_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing 8-K patterns: {e}")
            return {"error": str(e)}
    
    def _generate_risk_evolution_summary(self, risk_analysis: Dict) -> str:
        """Generate a summary of risk evolution trends."""
        if not risk_analysis:
            return "No risk data available for analysis."
        
        years = sorted(risk_analysis.keys())
        if len(years) < 2:
            return f"Only {len(years)} year(s) of data available for risk analysis."
        
        # Calculate trends
        first_year = years[0]
        last_year = years[-1]
        
        first_word_count = risk_analysis[first_year]['total_words']
        last_word_count = risk_analysis[last_year]['total_words']
        
        word_trend = "increased" if last_word_count > first_word_count else "decreased" if last_word_count < first_word_count else "remained stable"
        
        return f"Risk factor analysis shows {word_trend} from {first_year} to {last_year}. " \
               f"Total words: {first_word_count} → {last_word_count}. " \
               f"Filing frequency: {risk_analysis[first_year]['filing_count']} → {risk_analysis[last_year]['filing_count']} filings per year."
    
    def _generate_mdna_evolution_summary(self, mdna_analysis: Dict) -> str:
        """Generate a summary of MD&A evolution trends."""
        if not mdna_analysis:
            return "No MD&A data available for analysis."
        
        years = sorted(mdna_analysis.keys())
        if len(years) < 2:
            return f"Only {len(years)} year(s) of data available for MD&A analysis."
        
        # Calculate trends
        first_year = years[0]
        last_year = years[-1]
        
        first_word_count = mdna_analysis[first_year]['total_words']
        last_word_count = mdna_analysis[last_year]['total_words']
        
        word_trend = "increased" if last_word_count > first_word_count else "decreased" if last_word_count < first_word_count else "remained stable"
        
        return f"Management discussion analysis shows {word_trend} from {first_year} to {last_year}. " \
               f"Total words: {first_word_count} → {last_word_count}. " \
               f"Filing frequency: {mdna_analysis[first_year]['filing_count']} → {mdna_analysis[last_year]['filing_count']} filings per year."
    
    def _generate_comparative_risk_summary(self, comparison_data: Dict) -> str:
        """Generate a summary of comparative risk analysis."""
        if not comparison_data:
            return "No comparative data available."
        
        companies_with_data = [cik for cik, data in comparison_data.items() if data['filing_count'] > 0]
        
        if not companies_with_data:
            return "No risk factor data found for any of the specified companies."
        
        # Find company with most comprehensive risk discussion
        max_words = max(data['total_words'] for data in comparison_data.values() if data['filing_count'] > 0)
        most_comprehensive = [cik for cik, data in comparison_data.items() if data['total_words'] == max_words][0]
        
        return f"Comparative analysis of {len(companies_with_data)} companies. " \
               f"Company {most_comprehensive} has the most comprehensive risk discussion ({max_words} words). " \
               f"Average filings per company: {sum(data['filing_count'] for data in comparison_data.values()) / len(companies_with_data):.1f}."
    
    def _generate_8k_pattern_summary(self, item_analysis: Dict) -> str:
        """Generate a summary of 8-K event patterns."""
        if not item_analysis:
            return "No 8-K event data available for analysis."
        
        total_events = sum(data['count'] for data in item_analysis.values())
        most_common = max(item_analysis.items(), key=lambda x: x[1]['count'])
        
        return f"Total 8-K events: {total_events}. " \
               f"Most common event type: {most_common[0]} ({most_common[1]['title']}) with {most_common[1]['count']} occurrences. " \
               f"Unique event types: {len(item_analysis)}."
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()

# Convenience functions for easy integration with RAG system
def analyze_risk_evolution(company_cik: str, years: Optional[List[int]] = None) -> str:
    """Analyze how risk factors have evolved over time for a company."""
    engine = TemporalAnalysisEngine()
    result = engine.analyze_risk_evolution(company_cik, years)
    
    if 'error' in result:
        return f"Error: {result['error']}"
    
    # Format for RAG system
    summary = result['summary']
    yearly_data = result['yearly_breakdown']
    
    response = f"Risk Evolution Analysis for Company {company_cik} ({result['analysis_period']}):\n\n"
    response += f"Summary: {summary}\n\n"
    response += "Yearly Breakdown:\n"
    
    for year, data in sorted(yearly_data.items()):
        response += f"  {year}: {data['filing_count']} filings, {data['total_words']} words\n"
    
    return response

def analyze_management_view_evolution(company_cik: str, years: Optional[List[int]] = None) -> str:
    """Analyze how management's discussion has evolved over time."""
    engine = TemporalAnalysisEngine()
    result = engine.analyze_management_view_evolution(company_cik, years)
    
    if 'error' in result:
        return f"Error: {result['error']}"
    
    # Format for RAG system
    summary = result['summary']
    yearly_data = result['yearly_breakdown']
    
    response = f"Management View Evolution Analysis for Company {company_cik} ({result['analysis_period']}):\n\n"
    response += f"Summary: {summary}\n\n"
    response += "Yearly Breakdown:\n"
    
    for year, data in sorted(yearly_data.items()):
        response += f"  {year}: {data['filing_count']} filings, {data['total_words']} words\n"
    
    return response

def compare_company_risks(company_ciks: List[str], year: int) -> str:
    """Compare risk factors across multiple companies."""
    engine = TemporalAnalysisEngine()
    result = engine.compare_risk_factors_across_companies(company_ciks, year)
    
    if 'error' in result:
        return f"Error: {result['error']}"
    
    # Format for RAG system
    summary = result['summary']
    comparison_data = result['comparison_data']
    
    response = f"Comparative Risk Analysis for {year}:\n\n"
    response += f"Summary: {summary}\n\n"
    response += "Company Breakdown:\n"
    
    for cik, data in comparison_data.items():
        response += f"  Company {cik}: {data['filing_count']} filings, {data['total_words']} words\n"
    
    return response

def analyze_company_events(company_cik: str, months: int = 12) -> str:
    """Analyze 8-K event patterns for a company."""
    engine = TemporalAnalysisEngine()
    result = engine.analyze_8k_event_patterns(company_cik, months)
    
    if 'error' in result:
        return f"Error: {result['error']}"
    
    # Format for RAG system
    summary = result['summary']
    item_breakdown = result['item_breakdown']
    
    response = f"8-K Event Analysis for Company {company_cik} (Last {months} months):\n\n"
    response += f"Summary: {summary}\n\n"
    response += "Event Type Breakdown:\n"
    
    for item_type, data in sorted(item_breakdown.items(), key=lambda x: x[1]['count'], reverse=True):
        response += f"  {item_type} ({data['title']}): {data['count']} events\n"
    
    return response
