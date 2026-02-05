"""
URL Collection Module

Generates fixed and random Wikipedia URLs related to Indian history using the wikipedia library.
Saves URLs with metadata in JSON files.
"""

import wikipedia
import json
import random
import os
from typing import List, Dict

# Set language to English
wikipedia.set_lang("en")

def get_page_metadata(title: str) -> Dict:
    """Get metadata for a Wikipedia page."""
    try:
        page = wikipedia.page(title, auto_suggest=False)
        content = page.content
        word_count = len(content.split())
        return {
            "title": page.title,
            "url": page.url,
            "word_count": word_count,
            "summary": page.summary[:500],  # First 500 chars of summary
            "categories": page.categories[:10]  # First 10 categories
        }
    except wikipedia.exceptions.DisambiguationError as e:
        # If disambiguation, try the first option
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            content = page.content
            word_count = len(content.split())
            return {
                "title": page.title,
                "url": page.url,
                "word_count": word_count,
                "summary": page.summary[:500],
                "categories": page.categories[:10]
            }
        except:
            pass
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return None

def generate_fixed_urls(num_urls: int = 200) -> List[Dict]:
    """Generate fixed set of Indian history URLs with >200 words."""
    # List of famous Indian history topics/pages
    indian_history_topics = [
        "History of India", "Indus Valley Civilization", "Vedic period", "Maurya Empire",
        "Gupta Empire", "Delhi Sultanate", "Mughal Empire", "Maratha Empire",
        "British Raj", "Indian independence movement", "Partition of India",
        "Ashoka", "Chandragupta Maurya", "Akbar", "Mahatma Gandhi",
        "Sardar Vallabhbhai Patel", "Jawaharlal Nehru", "Sardar Bhagat Singh",
        "Rani Lakshmibai", "Mangal Pandey", "Bal Gangadhar Tilak",
        "Lala Lajpat Rai", "Bipin Chandra Pal", "Dadabhai Naoroji",
        "Satyagraha", "Non-cooperation movement", "Civil disobedience movement",
        "Quit India Movement", "Indian National Congress", "All India Muslim League",
        "Khilji dynasty", "Tughlaq dynasty", "Lodhi dynasty", "Sur Empire",
        "Chola dynasty", "Pallava dynasty", "Pandya dynasty", "Chera dynasty",
        "Kushans", "Shakas", "Western Kshatrapas", "Satavahana dynasty",
        "Western Chalukya Empire", "Rashtrakuta dynasty", "Hoysala Empire",
        "Vijayanagara Empire", "Bahmani Sultanate", "Deccan Sultanates",
        "Mysore Kingdom", "Travancore", "Hyderabad State", "Jammu and Kashmir (princely state)",
        "Bhutan", "Nepal", "Sri Lanka", "Maldives", "Indian Ocean trade",
        "Silk Road", "Spice trade", "Colonial India", "East India Company",
        "Battle of Plassey", "Battle of Buxar", "Sepoy Mutiny", "Indian Rebellion of 1857",
        "Government of India Act 1858", "Indian Councils Act 1892", "Indian Councils Act 1909",
        "Government of India Act 1919", "Government of India Act 1935", "Indian Independence Act 1947",
        "Constitution of India", "Republic of India", "Indian Army", "Indian Navy", "Indian Air Force",
        "Indian Space Research Organisation", "Bhabha Atomic Research Centre",
        "Indian Institutes of Technology", "Indian Institute of Science",
        "Aryabhata", "Bhaskara I", "Bhaskara II", "Varahamihira", "Brahmagupta",
        "Indian mathematics", "Indian astronomy", "Vedas", "Upanishads", "Ramayana", "Mahabharata",
        "Bhagavad Gita", "Puranas", "Buddhism", "Jainism", "Hinduism", "Sikhism", "Islam in India",
        "Christianity in India", "Zoroastrianism in India", "Judaism in India",
        "Ajanta Caves", "Ellora Caves", "Khajuraho", "Konark Sun Temple", "Taj Mahal",
        "Red Fort", "Qutub Minar", "India Gate", "Gateway of India", "Charminar",
        "Mysore Palace", "Hawa Mahal", "City Palace, Jaipur", "Amber Fort",
        "Golconda Fort", "Warangal Fort", "Chittorgarh Fort", "Kumbhalgarh",
        "Ranthambore Fort", "Jaisalmer Fort", "Mehrangarh Fort", "Junagarh Fort",
        "Lal Qila", "Agra Fort", "Fatehpur Sikri", "Humayun's Tomb", "Safdarjung's Tomb",
        "Rashtrapati Bhavan", "Parliament House (India)", "Supreme Court of India",
        "Reserve Bank of India", "Bombay Stock Exchange", "National Stock Exchange of India",
        "Indian Railways", "Indian postal service", "Indian telegraph", "Indian radio",
        "Indian television", "Indian cinema", "Bollywood", "Indian music", "Indian dance",
        "Indian cuisine", "Indian festivals", "Diwali", "Holi", "Durga Puja", "Eid al-Fitr",
        "Christmas in India", "Indian languages", "Hindi", "Bengali", "Telugu", "Marathi",
        "Tamil", "Urdu", "Gujarati", "Kannada", "Odia", "Punjabi", "Malayalam",
        "Assamese", "Maithili", "Sanskrit", "Pali", "Prakrit", "Dravidian languages",
        "Indo-Aryan languages", "Indian philosophy", "Indian logic", "Indian aesthetics",
        "Indian politics", "Indian economy", "Indian society", "Indian culture",
        "Caste system in India", "Untouchability", "Dalit", "Scheduled Castes and Scheduled Tribes",
        "Women's rights in India", "Child labour in India", "Education in India",
        "Health in India", "Poverty in India", "Unemployment in India", "Corruption in India",
        "Indian environmental issues", "Deforestation in India", "Pollution in India",
        "Climate change in India", "Natural disasters in India", "Earthquake", "Flood", "Cyclone",
        "Drought", "Indian wildlife", "National parks of India", "Tiger", "Elephant", "Lion",
        "Indian rivers", "Ganges", "Yamuna", "Brahmaputra", "Indus", "Godavari", "Krishna",
        "Cauvery", "Narmada", "Tapti", "Mahanadi", "Indian mountains", "Himalayas", "Western Ghats",
        "Eastern Ghats", "Aravalli Range", "Vindhya Range", "Satpura Range",
        "Indian deserts", "Thar Desert", "Indian oceans", "Arabian Sea", "Bay of Bengal",
        "Indian Ocean", "Andaman and Nicobar Islands", "Lakshadweep", "Puducherry",
        "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Ladakh", "Jammu and Kashmir",
        "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Ahmedabad",
        "Pune", "Surat", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
        "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad",
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivli",
        "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai",
        "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada",
        "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandrapur", "Solapur", "Hubballi-Dharwad",
        "Tiruchirappalli", "Bareilly", "Moradabad", "Mysore", "Tiruppur", "Gurgaon", "Aligarh",
        "Jalandhar", "Bhubaneswar", "Salem", "Mira-Bhayandar", "Warangal", "Thiruvananthapuram",
        "Bhiwandi", "Saharanpur", "Gorakhpur", "Guntur", "Bikaner", "Amravati", "Noida",
        "Jamshedpur", "Bhilai", "Cuttack", "Firozabad", "Kochi", "Nellore", "Bhavnagar",
        "Dehradun", "Durgapur", "Asansol", "Rourkela", "Nanded", "Kolhapur", "Ajmer", "Akola",
        "Gulbarga", "Jamnagar", "Ujjain", "Loni", "Siliguri", "Jhansi", "Ulhasnagar", "Jammu",
        "Sangli-Miraj & Kupwad", "Mangalore", "Erode", "Belgaum", "Ambattur", "Tirunelveli",
        "Malegaon", "Gaya", "Tirupati", "Davanagere", "Kozhikode", "Akbarpur", "Kurnool",
        "Rajpur Sonarpur", "Bokaro Steel City", "South Dumdum", "Bellary", "Patiala", "Gopalpur",
        "Agartala", "Bhagalpur", "Muzaffarnagar", "Bhatpara", "Panihati", "Latur", "Dhule",
        "Tiruvottiyur", "Korba", "Bhilwara", "Berhampur", "Muzaffarpur", "Ahmednagar", "Mathura",
        "Kollam", "Avadi", "Kadapa", "Kamarhati", "Sambalpur", "Bilaspur", "Shahjahanpur",
        "Satara", "Bijapur", "Rampur", "Shoreham-by-Sea", "Chandigarh", "Junagadh", "Thrissur",
        "Alwar", "Bardhaman", "Kulti", "Kakinada", "Nizamabad", "Parbhani", "Tumkur", "Khammam",
        "Ozhukarai", "Bihar Sharif", "Panipat", "Darbhanga", "Bally", "Aizawl", "Dewas", "Ichalkaranji",
        "Karnal", "Bathinda", "Jalna", "Eluru", "Kirari Suleman Nagar", "Barasat", "Purnia",
        "Satna", "Mau", "Sonipat", "Farrukhabad", "Sagar", "Rourkela", "Durg", "Imphal", "Ratlam",
        "Hapur", "Arrah", "Karimnagar", "Anantapur", "Etawah", "Ambarnath", "North Dumdum",
        "Bharatpur", "Begusarai", "New Delhi", "Gandhidham", "Baranagar", "Tiruvannamalai",
        "Pondicherry", "Sikar", "Thoothukudi", "Rewa", "Mirzapur", "Raichur", "Pallavaram",
        "Avaniapuram", "Kanchipuram", "Karaikudi", "Nagercoil", "Hosur", "Tanjore", "Pollachi",
        "Vellore", "Cuddalore", "Neyveli", "Thanjavur", "Kumbakonam", "Tiruchengode", "Salem",
        "Namakkal", "Dharmapuri", "Krishnagiri", "Tirupattur", "Ranipet", "Vaniyambadi",
        "Ambur", "Tiruppur", "Udumalaipettai", "Pollachi", "Valparai", "Mettupalayam", "Coonoor",
        "Ooty", "Gudalur", "Nilgiris", "Kodaikanal", "Palani", "Dindigul", "Madurai", "Theni",
        "Cumbum", "Bodinayakanur", "Periyakulam", "Usilampatti", "Andipatti", "Tiruchirappalli",
        "Thuraiyur", "Musiri", "Lalgudi", "Srirangam", "Tiruchirappalli", "Pudukkottai", "Aranthangi",
        "Pattukkottai", "Thiruvarur", "Nagapattinam", "Mayiladuthurai", "Sirkali", "Chidambaram",
        "Cuddalore", "Panruti", "Villupuram", "Tindivanam", "Gingee", "Tiruvannamalai", "Polur",
        "Arni", "Vellore", "Katpadi", "Gudiyatham", "Pallikonda", "Tiruttani", "Arakkonam",
        "Sholinghur", "Walajapet", "Kanchipuram", "Sriperumbudur", "Tambaram", "Chengalpattu",
        "Tirukalukundram", "Cheyyur", "Maduranthakam", "Uthiramerur", "Kattankulathur", "Chennai",
        "Tiruvallur", "Poonamallee", "Avadi", "Ambattur", "Tiruvottiyur", "Ennore", "Minjur",
        "Ponneri", "Gummidipoondi", "Uthukkottai", "Tiruppur", "Palladam", "Tiruppur", "Kangeyam",
        "Dharapuram", "Udumalaipettai", "Pollachi", "Valparai", "Mettupalayam", "Coonoor", "Ooty",
        "Gudalur", "Nilgiris", "Kodaikanal", "Palani", "Dindigul", "Madurai", "Theni", "Cumbum",
        "Bodinayakanur", "Periyakulam", "Usilampatti", "Andipatti", "Tiruchirappalli", "Thuraiyur",
        "Musiri", "Lalgudi", "Srirangam", "Tiruchirappalli", "Pudukkottai", "Aranthangi", "Pattukkottai",
        "Thiruvarur", "Nagapattinam", "Mayiladuthurai", "Sirkali", "Chidambaram", "Cuddalore",
        "Panruti", "Villupuram", "Tindivanam", "Gingee", "Tiruvannamalai", "Polur", "Arni", "Vellore",
        "Katpadi", "Gudiyatham", "Pallikonda", "Tiruttani", "Arakkonam", "Sholinghur", "Walajapet",
        "Kanchipuram", "Sriperumbudur", "Tambaram", "Chengalpattu", "Tirukalukundram", "Cheyyur",
        "Maduranthakam", "Uthiramerur", "Kattankulathur", "Chennai", "Tiruvallur", "Poonamallee",
        "Avadi", "Ambattur", "Tiruvottiyur", "Ennore", "Minjur", "Ponneri", "Gummidipoondi", "Uthukkottai"
    ]

    fixed_urls = []
    for topic in indian_history_topics[:num_urls]:
        metadata = get_page_metadata(topic)
        if metadata and metadata['word_count'] > 200:
            fixed_urls.append(metadata)
            print(f"Added fixed: {metadata['title']} ({metadata['word_count']} words)")
        if len(fixed_urls) >= num_urls:
            break

    # Save to file
    os.makedirs('data', exist_ok=True)
    with open('data/fixed_urls.json', 'w') as f:
        json.dump(fixed_urls, f, indent=2)

    print(f"Generated {len(fixed_urls)} fixed URLs.")
    return fixed_urls

def generate_random_urls(num_urls: int = 300) -> List[Dict]:
    """Generate random set of Indian history URLs with >200 words."""
    # Use a larger pool for randomness
    extended_topics = [
        "History of India", "Indus Valley Civilization", "Vedic period", "Maurya Empire",
        "Gupta Empire", "Delhi Sultanate", "Mughal Empire", "Maratha Empire",
        "British Raj", "Indian independence movement", "Partition of India",
        "Ashoka", "Chandragupta Maurya", "Akbar", "Mahatma Gandhi",
        "Sardar Vallabhbhai Patel", "Jawaharlal Nehru", "Sardar Bhagat Singh",
        "Rani Lakshmibai", "Mangal Pandey", "Bal Gangadhar Tilak",
        "Lala Lajpat Rai", "Bipin Chandra Pal", "Dadabhai Naoroji",
        "Satyagraha", "Non-cooperation movement", "Civil disobedience movement",
        "Quit India Movement", "Indian National Congress", "All India Muslim League",
        "Khilji dynasty", "Tughlaq dynasty", "Lodhi dynasty", "Sur Empire",
        "Chola dynasty", "Pallava dynasty", "Pandya dynasty", "Chera dynasty",
        "Kushans", "Shakas", "Western Kshatrapas", "Satavahana dynasty",
        "Western Chalukya Empire", "Rashtrakuta dynasty", "Hoysala Empire",
        "Vijayanagara Empire", "Bahmani Sultanate", "Deccan Sultanates",
        "Mysore Kingdom", "Travancore", "Hyderabad State", "Jammu and Kashmir (princely state)",
        "Bhutan", "Nepal", "Sri Lanka", "Maldives", "Indian Ocean trade",
        "Silk Road", "Spice trade", "Colonial India", "East India Company",
        "Battle of Plassey", "Battle of Buxar", "Sepoy Mutiny", "Indian Rebellion of 1857",
        "Government of India Act 1858", "Indian Councils Act 1892", "Indian Councils Act 1909",
        "Government of India Act 1919", "Government of India Act 1935", "Indian Independence Act 1947",
        "Constitution of India", "Republic of India", "Indian Army", "Indian Navy", "Indian Air Force",
        "Indian Space Research Organisation", "Bhabha Atomic Research Centre",
        "Indian Institutes of Technology", "Indian Institute of Science",
        "Aryabhata", "Bhaskara I", "Bhaskara II", "Varahamihira", "Brahmagupta",
        "Indian mathematics", "Indian astronomy", "Vedas", "Upanishads", "Ramayana", "Mahabharata",
        "Bhagavad Gita", "Puranas", "Buddhism", "Jainism", "Hinduism", "Sikhism", "Islam in India",
        "Christianity in India", "Zoroastrianism in India", "Judaism in India",
        "Ajanta Caves", "Ellora Caves", "Khajuraho", "Konark Sun Temple", "Taj Mahal",
        "Red Fort", "Qutub Minar", "India Gate", "Gateway of India", "Charminar",
        "Mysore Palace", "Hawa Mahal", "City Palace, Jaipur", "Amber Fort",
        "Golconda Fort", "Warangal Fort", "Chittorgarh Fort", "Kumbhalgarh",
        "Ranthambore Fort", "Jaisalmer Fort", "Mehrangarh Fort", "Junagarh Fort",
        "Lal Qila", "Agra Fort", "Fatehpur Sikri", "Humayun's Tomb", "Safdarjung's Tomb",
        "Rashtrapati Bhavan", "Parliament House (India)", "Supreme Court of India",
        "Reserve Bank of India", "Bombay Stock Exchange", "National Stock Exchange of India",
        "Indian Railways", "Indian postal service", "Indian telegraph", "Indian radio",
        "Indian television", "Indian cinema", "Bollywood", "Indian music", "Indian dance",
        "Indian cuisine", "Indian festivals", "Diwali", "Holi", "Durga Puja", "Eid al-Fitr",
        "Christmas in India", "Indian languages", "Hindi", "Bengali", "Telugu", "Marathi",
        "Tamil", "Urdu", "Gujarati", "Kannada", "Odia", "Punjabi", "Malayalam",
        "Assamese", "Maithili", "Sanskrit", "Pali", "Prakrit", "Dravidian languages",
        "Indo-Aryan languages", "Indian philosophy", "Indian logic", "Indian aesthetics",
        "Indian politics", "Indian economy", "Indian society", "Indian culture",
        "Caste system in India", "Untouchability", "Dalit", "Scheduled Castes and Scheduled Tribes",
        "Women's rights in India", "Child labour in India", "Education in India",
        "Health in India", "Poverty in India", "Unemployment in India", "Corruption in India",
        "Indian environmental issues", "Deforestation in India", "Pollution in India",
        "Climate change in India", "Natural disasters in India", "Earthquake", "Flood", "Cyclone",
        "Drought", "Indian wildlife", "National parks of India", "Tiger", "Elephant", "Lion",
        "Indian rivers", "Ganges", "Yamuna", "Brahmaputra", "Indus", "Godavari", "Krishna",
        "Cauvery", "Narmada", "Tapti", "Mahanadi", "Indian mountains", "Himalayas", "Western Ghats",
        "Eastern Ghats", "Aravalli Range", "Vindhya Range", "Satpura Range",
        "Indian deserts", "Thar Desert", "Indian oceans", "Arabian Sea", "Bay of Bengal",
        "Indian Ocean", "Andaman and Nicobar Islands", "Lakshadweep", "Puducherry",
        "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Ladakh", "Jammu and Kashmir",
        "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", "Hyderabad", "Ahmedabad",
        "Pune", "Surat", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
        "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad",
        "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivli",
        "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai",
        "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada",
        "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandrapur", "Solapur", "Hubballi-Dharwad",
        "Tiruchirappalli", "Bareilly", "Moradabad", "Mysore", "Tiruppur", "Gurgaon", "Aligarh",
        "Jalandhar", "Bhubaneswar", "Salem", "Mira-Bhayandar", "Warangal", "Thiruvananthapuram",
        "Bhiwandi", "Saharanpur", "Gorakhpur", "Guntur", "Bikaner", "Amravati", "Noida",
        "Jamshedpur", "Bhilai", "Cuttack", "Firozabad", "Kochi", "Nellore", "Bhavnagar",
        "Dehradun", "Durgapur", "Asansol", "Rourkela", "Nanded", "Kolhapur", "Ajmer", "Akola",
        "Gulbarga", "Jamnagar", "Ujjain", "Loni", "Siliguri", "Jhansi", "Ulhasnagar", "Jammu",
        "Sangli-Miraj & Kupwad", "Mangalore", "Erode", "Belgaum", "Ambattur", "Tirunelveli",
        "Malegaon", "Gaya", "Tirupati", "Davanagere", "Kozhikode", "Akbarpur", "Kurnool",
        "Rajpur Sonarpur", "Bokaro Steel City", "South Dumdum", "Bellary", "Patiala", "Gopalpur",
        "Agartala", "Bhagalpur", "Muzaffarnagar", "Bhatpara", "Panihati", "Latur", "Dhule",
        "Tiruvottiyur", "Korba", "Bhilwara", "Berhampur", "Muzaffarpur", "Ahmednagar", "Mathura",
        "Kollam", "Avadi", "Kadapa", "Kamarhati", "Sambalpur", "Bilaspur", "Shahjahanpur",
        "Satara", "Bijapur", "Rampur", "Shoreham-by-Sea", "Chandigarh", "Junagadh", "Thrissur",
        "Alwar", "Bardhaman", "Kulti", "Kakinada", "Nizamabad", "Parbhani", "Tumkur", "Khammam",
        "Ozhukarai", "Bihar Sharif", "Panipat", "Darbhanga", "Bally", "Aizawl", "Dewas", "Ichalkaranji",
        "Karnal", "Bathinda", "Jalna", "Eluru", "Kirari Suleman Nagar", "Barasat", "Purnia",
        "Satna", "Mau", "Sonipat", "Farrukhabad", "Sagar", "Rourkela", "Durg", "Imphal", "Ratlam",
        "Hapur", "Arrah", "Karimnagar", "Anantapur", "Etawah", "Ambarnath", "North Dumdum",
        "Bharatpur", "Begusarai", "New Delhi", "Gandhidham", "Baranagar", "Tiruvannamalai",
        "Pondicherry", "Sikar", "Thoothukudi", "Rewa", "Mirzapur", "Raichur", "Pallavaram",
        "Avaniapuram", "Kanchipuram", "Karaikudi", "Nagercoil", "Hosur", "Tanjore", "Pollachi",
        "Vellore", "Cuddalore", "Neyveli", "Thanjavur", "Kumbakonam", "Tiruchengode", "Salem",
        "Namakkal", "Dharmapuri", "Krishnagiri", "Tirupattur", "Ranipet", "Vaniyambadi",
        "Ambur", "Tiruppur", "Udumalaipettai", "Pollachi", "Valparai", "Mettupalayam", "Coonoor",
        "Ooty", "Gudalur", "Nilgiris", "Kodaikanal", "Palani", "Dindigul", "Madurai", "Theni",
        "Cumbum", "Bodinayakanur", "Periyakulam", "Usilampatti", "Andipatti", "Tiruchirappalli",
        "Thuraiyur", "Musiri", "Lalgudi", "Srirangam", "Tiruchirappalli", "Pudukkottai", "Aranthangi",
        "Pattukkottai", "Thiruvarur", "Nagapattinam", "Mayiladuthurai", "Sirkali", "Chidambaram",
        "Cuddalore", "Panruti", "Villupuram", "Tindivanam", "Gingee", "Tiruvannamalai", "Polur",
        "Arni", "Vellore", "Katpadi", "Gudiyatham", "Pallikonda", "Tiruttani", "Arakkonam",
        "Sholinghur", "Walajapet", "Kanchipuram", "Sriperumbudur", "Tambaram", "Chengalpattu",
        "Tirukalukundram", "Cheyyur", "Maduranthakam", "Uthiramerur", "Kattankulathur", "Chennai",
        "Tiruvallur", "Poonamallee", "Avadi", "Ambattur", "Tiruvottiyur", "Ennore", "Minjur",
        "Ponneri", "Gummidipoondi", "Uthukkottai", "Tiruppur", "Palladam", "Tiruppur", "Kangeyam",
        "Dharapuram", "Udumalaipettai", "Pollachi", "Valparai", "Mettupalayam", "Coonoor", "Ooty",
        "Gudalur", "Nilgiris", "Kodaikanal", "Palani", "Dindigul", "Madurai", "Theni", "Cumbum",
        "Bodinayakanur", "Periyakulam", "Usilampatti", "Andipatti", "Tiruchirappalli", "Thuraiyur",
        "Musiri", "Lalgudi", "Srirangam", "Tiruchirappalli", "Pudukkottai", "Aranthangi", "Pattukkottai",
        "Thiruvarur", "Nagapattinam", "Mayiladuthurai", "Sirkali", "Chidambaram", "Cuddalore",
        "Panruti", "Villupuram", "Tindivanam", "Gingee", "Tiruvannamalai", "Polur", "Arni", "Vellore",
        "Katpadi", "Gudiyatham", "Pallikonda", "Tiruttani", "Arakkonam", "Sholinghur", "Walajapet",
        "Kanchipuram", "Sriperumbudur", "Tambaram", "Chengalpattu", "Tirukalukundram", "Cheyyur",
        "Maduranthakam", "Uthiramerur", "Kattankulathur", "Chennai", "Tiruvallur", "Poonamallee",
        "Avadi", "Ambattur", "Tiruvottiyur", "Ennore", "Minjur", "Ponneri", "Gummidipoondi", "Uthukkottai"
    ] * 2  # Duplicate to have more

    random.shuffle(extended_topics)
    random_urls = []
    seen_titles = set()
    for topic in extended_topics:
        if len(random_urls) >= num_urls:
            break
        if topic in seen_titles:
            continue
        metadata = get_page_metadata(topic)
        if metadata and metadata['word_count'] > 200 and metadata['title'] not in seen_titles:
            random_urls.append(metadata)
            seen_titles.add(metadata['title'])
            print(f"Added random: {metadata['title']} ({metadata['word_count']} words)")

    # Save to file
    with open('data/random_urls.json', 'w') as f:
        json.dump(random_urls, f, indent=2)

    print(f"Generated {len(random_urls)} random URLs.")
    return random_urls

if __name__ == "__main__":
    # Generate fixed URLs only if file doesn't exist or has fewer than 200 URLs
    if not os.path.exists('data/fixed_urls.json'):
        print("Generating fixed URLs...")
        generate_fixed_urls()
    else:
        with open('data/fixed_urls.json', 'r') as f:
            existing_data = json.load(f)
        if len(existing_data) < 200:
            print(f"Existing fixed URLs file has only {len(existing_data)} URLs, regenerating...")
            generate_fixed_urls()
        else:
            print("Fixed URLs already exist with sufficient count. Skipping generation.")

    # Random URLs are generated when needed in data_collection.py