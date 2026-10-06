"""Adapt the existing mirror's content without replacing its design or animation hooks.

Re-runs always start from verification/product-before, never from generated HTML.
"""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import json
import re
import shutil
from refresh_rover_media import update_media

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / 'verification/product-before'
SITE = ROOT / 'site'
ASSET = '/_assets/metrix/'
DOC = ASSET + 'MetriX-AI-Product-Introduction-CN.docx'
PHOTO = ASSET + 'rover-reference.webp'

def norm(s):
    return ' '.join(s.replace('\u200d', '').split())

COPY = {
    'MetriX': 'MetriX AI',
    'Edificio Puerta Bajío, Piso 7 León, Guanajuato, México': 'Industry pilots · Data-led collaboration',
    '+ 1.000.000 linear meters': 'Prototype & proof of concept',
    '+ 837.650 linear meters': 'Prototype & proof of concept',
    'Map of our projects in Mexico': 'Potential pilot applications',
    'Our Services': 'AI Solutions', 'Our services': 'AI solutions',
    'Technology': 'Smart Rover', 'Safety': 'Validation', 'Safety Policy': 'Human-reviewed AI',
    'About us': 'About MetriX', 'About Us': 'About MetriX', 'Blog': 'Insights',
    'Join the Team': 'Pilot Partners', 'Join the team': 'Pilot partners',
    'Your trusted partner': 'Mine Smarter.', 'in underground mining': 'Verify Better. Recover More.',
    'Underground mining services': 'Data-led mining decisions',
    'Over time': 'Decision platform', '+ 1.000.000': '3 AI modules', '+ 837.650': '3 AI modules',
    'linear meters': 'One connected vision',
    'Engineering': 'MineFit AI', 'Ground Support & Fortification': 'QualityGuard AI',
    'Development': 'CircularMine AI', 'Production': 'Smart Sampling Rover', 'Hauling': 'Enterprise Integration',
    "We design and plan safe, efficient, and sustainable underground mining infrastructure tailored to each project's geological and operational conditions.":
        'Match equipment to tasks and compare transport routes using capacity, road conditions, energy and availability.',
    'We stabilize underground workings using anchors, mesh, shotcrete, and steel frames to secure fractured or high-risk ground.':
        'Identify ore variability, recommend sampling coverage and connect each sample to its source and laboratory results.',
    'We execute precise tunnel development for ramps and access points using drilling, blasting, and excavation techniques.':
        'Compare recovery pathways for tailings and by-products using measured grades, recovery assumptions, prices and costs.',
    'We extract mineralized material through controlled stoping methods optimized for productivity, dilution control, and safety.':
        'Explore our rover concept for image capture, assisted sampling and sample records, linked to QualityGuard AI.',
    'We transport blasted ore and waste using scooptrams, low-profile trucks, and efficient underground logistics systems.':
        'Start with a scoped pilot. Plan validated module subscriptions, private deployment and integration around your data.',
    'Minerals we extract': 'Potential mineral applications', 'Minerals We Extract': 'Materials We Study',
    'Minerals': 'Materials',
    'Gold : 600 Tonnes mined in 2025': 'Gold: illustrative material; scenario validation required.',
    'Silver : 588 Tonnes mined in 2024': 'Silver: illustrative material; scenario validation required.',
    'Lead : 731 Tonnes mined in 2025': 'Lead: illustrative material; scenario validation required.',
    'Copper : 854 Tonnes mined in 2023': 'Copper: potential application, subject to data validation.',
    'Zinc : 312 Tonnes mined in 2022': 'Zinc: potential application, subject to data validation.',
    'Over 360 machines': 'Smart sampling rover', 'for underground performance': 'A concept for the field',
    'Our Fleet': 'Explore the Rover', 'See more about our fleet': 'Explore our rover concept',
    'See more about our services': 'Explore MetriX AI solutions',
    'learn more about our services': 'Learn more about MetriX AI modules',
    'See more about technology': 'Explore the smart sampling rover',
    'See more about our safety policy': 'Explore our validation approach',
    'Read more about our safety policy': 'Read about human review and validation',
    'See more about safety': 'Explore validation', 'See more about our company': 'About the MetriX AI project',
    'See more about us': 'About the MetriX AI project',
    'Our Team': 'Our Approach', 'Our strength is our people': 'Evidence guides every decision',
    'Operation': 'MineFit AI', 'Quality Processes': 'QualityGuard AI', 'Quality processes': 'QualityGuard AI',
    'Security': 'Human Review', 'Maintenance': 'CircularMine AI',
    'Administration & ressources': 'Field Sampling', 'Administration': 'Field Sampling', 'Resources': 'Integration',
    'Job offers': 'Pilot opportunities', 'See our job offers': 'Explore pilot opportunities',
    'See more about our job offers': 'Explore pilot opportunities',
    'Our Partners': 'Who We Serve',
    'info@cominvi.com': 'Product introduction', '+52 477 690 4050': 'Prepare a pilot brief',
    '2026 MetriX - Designed and developed by Holographik®': '2026 MetriX AI · Prototype & proof of concept',
    'Notice of Privacy': 'Data & Product Scope', 'Legal': 'Information',
    'At the cutting edge': 'Intelligence meets', 'of technology': 'the field.',
    'More than 360 specialized': 'Smart Sampling Rover', 'underground mining units': 'Hardware concept · 3D demo',
    'Latest TECHNOLOGY': 'Rover concept', 'Our latest technology': 'Inside the rover',
    'Brands': 'Platform Modules', 'Workshops': 'Development Path',
    'Maintenance Infrastructure': 'Mechanical validation', 'Central service workshop': 'Controlled mobility',
    'On-Site service workshops': 'Platform connection',
    'Development & Drilling': 'Perception & Analysis', 'Haulage & Loading': 'Mobility & Records',
    'Ground Support & Construction': 'Sampling & Handling', 'Operational Support': 'Platform Connection',
    '20 years of business': 'A clearer view of', 'strength and experience': 'mining decisions.',
    'Our History': 'Our Roadmap', 'From 1934': 'From 2027', 'To 2025': 'To 2029',
    'The story of a Family': 'From prototype to pilot', 'The Redline': 'Our Purpose', 'Ethics': 'Evidence',
    'Social Impact': 'Validation Milestones', 'Our Certifications': 'Our validation priorities',
    'Socially Responsible Company (ESR)': 'Reproducible prototypes',
    'ISO 45001:2018 & ISO 9001:2015': 'Expert-reviewed pilots',
    'United Nations Global Compact': 'Validated module delivery',
    'Risk & Process Mapping': 'Data & Assumptions',
    'Our Projects': 'Use Cases', 'Client': 'User', 'Location': 'Focus',
    'Our Process': 'Pilot Process',
    'Chispas': 'Route Planning', 'Pinos Altos': 'Equipment Matching', 'Concheño': 'Sampling Coverage',
    'Aranzazu': 'Sample Traceability', 'Cozamin': 'Resource Screening', 'Campo Morado': 'Recovery Comparison',
    'Don David Gold': 'Rover Validation',
    'Silver Crest': 'Mining Operators', 'Agnico Eagle': 'Dispatch Teams', 'Minera Frisco': 'Testing Organisations',
    'Aura Minerals Inc.': 'Quality Teams', 'Capstone Mining Corp': 'Recovery Businesses',
    'Luca Mining Corp': 'Process Engineers', 'Gold Resources Corp': 'Field Teams',
    'Sonora': 'MineFit AI', 'Chihuahua': 'Scenario pilot', 'Zacatecas': 'Data validation',
    'Guerrero': 'CircularMine AI', 'Oaxaca': 'Controlled testing',
    'Drilling': 'Define the scenario', 'Blasting': 'Prepare the data', 'Mucking': 'Check the baseline',
    'Haulage': 'Run offline analysis', 'Ground Support': 'Review recommendations',
    'Continuous Execution': 'Compare scenarios', 'Ventilation': 'Test sensitivity',
    'Scaling/Re-scaling': 'Run a scoped pilot', 'Supervision': 'Evaluate results',
    'Safety Monitoring': 'Agree next steps',
    'CCRM': 'Evidence & Review', 'Commitment': 'Human Oversight',
    'Improvement & Well-being': 'Validation & Learning',
    'Policies & Procedures': 'Data Provenance', 'Digital Management Tools': 'Sample Traceability',
    'Program Administration': 'Model Review',
    'Rafael Villagómez': 'MetriX AI', 'Chairman of the Board at MetriX': 'Product principle',
    'Central Office': 'Start a Pilot', 'Tel': 'Next step', 'Mail': 'Read more', 'Address': 'Initial focus',
    'Drop us a line': 'Prepare your pilot brief', 'How can we help?': 'Describe your scenario. Download a brief to share with the team.',
    'Send': 'Download brief', 'THANK YOU': 'BRIEF READY · SAVED LOCALLY',
    'Oops! Something went wrong while submitting the form.': 'Your brief could not be created. Please try again.',
    'Open Positions': 'Pilot Opportunities', 'Work Team': 'Industry Collaboration',
    'Our strength,': 'Start with a scenario,', 'is our people®': 'validate its value.',
    'We are a family of': 'Built around', 'Over 1.700 collaborators': '3 connected AI modules',
    'Mining Engineer': 'Industry Pilot Partner',
    'Gender Equity': 'Pilot Priorities', 'Gender': 'Data', 'Equity': 'Review',
    '35%': '01', '65%': '02', 'Women in mine': 'Data preparation', 'Women in administration': 'Expert review',
    'University': 'Product Guide',
    'November 13, 2025': 'Product overview', 'November 12, 2025': 'Product guide',
    'Safety First: How MetriX Builds a Culture of Protection Underground': 'QualityGuard AI: Better Sampling Starts with Coverage',
    'Open-Pit vs. Underground Mining: Two Worlds Beneath the Same Goal': 'MineFit AI: Match Equipment, Compare Routes',
    'CCRM Bootcamp: Leadership in Action, Every Shift': 'CircularMine AI: Compare Secondary Resource Value',
    'In underground mining, safety is not just a regulation — it’s a way of life.': 'QualityGuard AI connects ore variability, sampling coverage and laboratory evidence.',
    'Mining has always been about extracting the Earth’s hidden treasures—but the way we reach them makes all the difference': 'MineFit AI compares feasible equipment and routes against task requirements and operating constraints.',
    'The first MetriX Bootcamp brought together Directors, Managers, and Safety Coordinators with one clear purpose: to strengthen the implementation of our Critical Risk Management System (CCRM) and reinforce the leadership commitment that defines our company': 'CircularMine AI compares recovery options using measured grades, recovery assumptions, prices and processing costs.',
}

PREFIX = {
    'From our roots in Guanajuato': 'MetriX AI is at the prototype and proof-of-concept stage. We invite industry partners to validate one clear scenario before expanding the platform.',
    'MetriX is a leading underground mining contractor': 'MetriX AI turns mining, visual and laboratory data into explainable decisions for operations, sampling and secondary resource recovery.',
    'With over 20 years of experience': 'MineFit AI, QualityGuard AI and CircularMine AI connect three key decisions: equipment allocation, representative sampling and resource value.',
    'We combine a strong safety culture': 'Start with one module and your existing data. The project is at the prototype and proof-of-concept stage; wider delivery follows validation.',
    'Leveraging our deep geological insight': 'Three AI modules connect planning, quality verification and recovery assessment. Begin with one measurable problem and validate the result.',
    'At MetriX, we are convinced': 'Every recommendation should explain its data, constraints and assumptions. Professional review remains central to important decisions.',
    'To this end, we are committed': 'Visual features support sampling decisions; laboratory testing confirms composition and quality.',
    'Our underground fleet features': 'The MetriX Smart Sampling Rover concept connects image capture, assisted sampling and sample records with QualityGuard AI.',
    'We operate leading brands': 'Explore the six-wheel rover, articulated sampling arm, sample carousel and sensor mast. Hardware capabilities remain subject to engineering and field validation.',
    '“I enjoy working at this company': '“Make the recommendation understandable: show its source data, assumptions and constraints.”',
    'by Juan Erasmo': 'MetriX AI · Explainable decisions',
    '“Thanks to MetriX': '“Start with one clear scenario, compare against a baseline, then expand on evidence.”',
    'by Sebastián': 'MetriX AI · Measurable pilots',
    'Leading mining companies trust': 'We invite mining operators, testing organisations and resource recovery businesses to develop a clearly scoped pilot together.',
    'We deliver comprehensive underground': 'From equipment scheduling to sampling and recovery assessment, our modules help teams compare options and understand the evidence behind each recommendation.',
    'Our focus is on safety': 'Proposed services include scoped pilots, validated module subscriptions, enterprise deployment and model customisation.',
    'MetriX currently operates in 7': 'Seven example use cases illustrate where a scoped pilot could begin. These are proposed applications, not customer deployments.',
    'At the Las Chispas project': 'MineFit AI compares feasible transport routes using distance, slope, congestion and energy assumptions. Operators review the expected time and cost before selecting a route. A pilot compares the recommendations with existing rules under the same tasks and fleet constraints.',
    'At the heart of the Sierra Madre': 'Match tasks to equipment using payload, position, availability and road access. MineFit AI first excludes infeasible choices, then compares workable combinations. Outdated equipment status and insufficient capacity are flagged for review.',
    'Since June 2025': 'QualityGuard AI identifies differences in ore images and suggests sampling locations based on coverage, variability and budget. Visual clusters describe feature differences; they are not direct measurements of metal grade. Laboratory evidence and expert review remain essential.',
    'Since 2018, MetriX': 'Link each sample to a batch, location, collection time and laboratory result. The planned workflow helps teams investigate unexpected results and identify missing coverage. Sample identifiers, handling and contamination controls must be validated for each field scenario.',
    'In Cozamin, MetriX': 'CircularMine AI screens tailings and suitable by-products using dry quantity, measured grade, recovery assumptions and costs. It identifies candidates for additional tests. Original ore grades cannot substitute for the corresponding tailings measurements.',
    'Since August 2024': 'Compare suitable recovery pathways and observe how prices, recovery rates and costs affect their ranking. Estimated net operating value supports early screening; investment decisions require additional capital, financing and cash-flow analysis.',
    'MetriX began operations at Don David': 'The Smart Sampling Rover is a concept hardware extension. First validate mechanical sampling, storage and identifiers; then controlled mobility and remote operation; finally limited-area navigation and platform integration. The model illustrates the design, not certified performance.',
    'At MetriX, underground mining is a coordinated': 'A pilot starts with a measurable scenario and agreed baseline. Prepare the data, run offline analysis, review the results with domain experts and expand only after the agreed indicators have been validated.',
    'This is the process of creating boreholes': 'Agree the operational question, boundaries, users and measurable acceptance criteria.',
    'The controlled use of explosives': 'Collect the relevant maps, equipment parameters, images, sample records or recovery assumptions.',
    'The process of cleaning and extracting': 'Record the current approach and distinguish measured data from simulated inputs.',
    'The transportation of blasted material': 'Run the selected module against a fixed task and retain the input and parameter versions.',
    'A technique used to ensure ground stability': 'Ask dispatch, sampling or process specialists to check recommendations against site conditions.',
    'The continuous coordination and execution': 'Compare the recommended options with the baseline using consistent units and constraints.',
    'The injection of clean, fresh air': 'Change key prices, recovery rates or operating assumptions to understand result sensitivity.',
    'A technique used to detect and safely remove': 'Use reviewed recommendations in an agreed, limited scope and record actual outcomes.',
    'The inspection and verification of the quality': 'Check the agreed indicators, exceptions and applicability limits with the customer team.',
    'A process involving the observation and analysis': 'Decide whether the evidence supports continued use, additional validation or a revised scope.',
    'MetriX operates a fleet of over': 'Our Smart Sampling Rover is a planned hardware extension for QualityGuard AI. Its concept combines a six-wheel chassis, vision and scanning sensors, an articulated arm and sample storage.',
    'Our fleet is powered by top-tier': 'MineFit AI supports operations, QualityGuard AI supports sampling, and CircularMine AI supports recovery assessment. The rover is a planned field interface to this modular platform.',
    'At our company, maintenance is not': 'Begin with mechanical sampling, sample storage and reliable identifiers. Confirm sample handling and contamination controls in a controlled setting before advancing to mobility.',
    'Our central facility is equipped': 'Validate controlled movement and remote operation against the selected site conditions. Navigation, communications and safe stopping need dedicated engineering tests.',
    'Each of our project sites features': 'Connect reviewed sampling tasks, captured images and sample records to QualityGuard AI. Validate limited-area navigation and integration only after the earlier hardware stages pass.',
    'Our commitment to maintenance excellence': 'The 3D model and images illustrate a concept. Endurance, payload, slope capability, protection rating and positioning accuracy are not established specifications.',
    'A company built on history': 'A modular decision-support platform for non-ferrous and critical metals. MetriX AI connects mining operations, quality verification and secondary resource assessment through traceable data.',
    'The story of MetriX begins in 1934': '2027 · Prototype validation. Build reproducible simulations for all three modules and seek expert and academic feedback.',
    'His son, Rafael': 'The next stage requires clear data boundaries, repeatable demonstrations and documented model assumptions.',
    'In 1997, Lic.': '2028 · Industry proof of concept. Select one operational, testing or recovery scenario for a pilot using real data.',
    'With hands-on experience': 'Agree the baseline and acceptance indicators with the business team before running the pilot.',
    'In 2002, MetriX': '2029 · Modular commercial expansion. Prioritise the most validated module, then extend services and enterprise integration.',
    'Since then, we’ve grown': 'These are planned stages. Progress depends on repeatable delivery, operational capability and evidence from continued use.',
    'We are a construction company specialized': 'Our mission is to turn scattered mining data into understandable actions, helping teams use resources more efficiently, strengthen quality decisions and assess recovery opportunities.',
    'To be recognized as global leaders': 'Our vision is to become a daily decision-support tool for non-ferrous and critical metals businesses, connecting operations, quality and recovery teams around data with clear provenance.',
    'At MetriX, ethical conduct': 'Recommendations should show the data, constraints and assumptions behind them. Keep professional review in the loop and request more evidence when a model has insufficient grounds to recommend an action.',
    'At MetriX, responsible mining begins': 'CircularMine AI compares potential recovery options for tailings and suitable by-products. Measured grades, trial recovery data and processing costs provide the basis for each scenario.',
    'Though we operate underground': 'Assess environmental benefits through verifiable energy, transport and resource-use records. No fixed savings or emission reduction percentage is assumed.',
    'Properly executed underground mining': 'A promising resource value is a starting point for additional testing. Material performance, environmental requirements and site conditions still need review.',
    'Our commitment is clear': 'Use evidence to decide which opportunities deserve further testing and development.',
    'We believe true excellence is earned': 'Product progress is assessed through reproducible simulations, expert review and scoped field pilots. These are validation priorities, not certifications or completed deployments.',
    'For the tenth consecutive year': 'Record input data, parameter versions and exceptions so the prototype results can be repeated and checked independently.',
    'At MetriX, safety and quality go hand': 'Use real scenario data, an agreed baseline and professional review to assess whether a module meets the pilot criteria.',
    'In line with the 10 Principles': 'Expand a validated module only when its scope, support requirements and repeatability are clear. Wider enterprise deployment is a proposed productisation direction.',
    'Tailored risk management adapted': 'Record data sources, units, dates and model assumptions. Compare scenario results and require review when inputs fall outside the validated operating range.',
    '"You can count on me': '"Explain the evidence. Review the recommendation. Validate the result."',
    'For the first time in our history': 'MetriX AI is at the prototype and proof-of-concept stage. Each module is designed to support professional judgment through explainable recommendations and traceable inputs.',
    'This system is a key step': 'Define the baseline, input quality and acceptance criteria before a pilot. Compare results under equivalent tasks and distinguish simulated values from measured outcomes.',
    'At MetriX, safety is not just': 'Human review is a core product principle. A recommendation with insufficient evidence should request more data or pause.',
    'At MetriX, safety begins': 'Important operational, sampling and recovery decisions stay with qualified people. The platform helps compare options and understand constraints.',
    'We are committed to providing our team': 'Image clusters show visual differences; they do not certify metal grade. Surface images cannot fully describe the internal layers of an ore pile.',
    'We firmly believe that all workplace': 'Formal sampling plans and laboratory methods remain essential to confirming composition and quality.',
    'That is why we focus our efforts': 'Recovery estimates depend on measured grades, applicable recovery tests and current cost assumptions. They do not establish investment feasibility on their own.',
    'Because at MetriX': 'Every result should state its applicable scope and the evidence still required.',
    'At MetriX, continuous improvement': 'Validation combines repeatable offline analysis with professional review and a limited, agreed field scope. Actual outcomes and exceptions inform the next iteration.',
    'We provide innovative tools': 'Track route cost and constraint violations, sampling coverage and test differences, or recovery calculation consistency according to the selected module.',
    'We work daily to ensure compliance': 'Keep simulated inputs separate from measured data. Document sources, units, versions and assumptions alongside each result.',
    'This commitment is embedded': 'The proposed productisation approach connects four practical controls:',
    'Structured formats and preventive techniques': 'Record source, collection time, units and applicable scope for each input.',
    'A centralized platform for reporting incidents': 'Connect sample identifiers, batches, locations and laboratory results.',
    'A unified interface to manage health': 'Preserve model versions, assumptions and professional review decisions.',
    'Blvd. Paseo': 'Guangxi · Non-ferrous and critical metals. Initial cooperation focus; no public office address has been provided.',
    'At MetriX, we employ enthusiasts': 'We seek industry partners with a clear scenario, relevant data and professional feedback. Start with one measurable problem and agree the pilot scope together.',
    'Your safety is our priority': 'Validation comes before expansion. Agree data access, expert review and acceptance criteria for the selected scenario. Rover-related work follows separate hardware and field validation.',
    'Rorem ipsum': 'Share a defined operational, testing or recovery scenario. A proposed pilot combines your data and domain feedback with module analysis, baseline comparison and a documented result.',
    'Lorem ipsum': 'Concept capability. Engineering, data quality and scenario validation determine the final delivery scope.',
}

MACHINES = [
    ('Motor Grader', 'Six-Wheel Chassis', 'Six articulated wheel assemblies form the mobility concept. Terrain suitability must be verified in controlled field tests.'),
    ('Air Compressor', 'Emergency Stop', 'The exterior concept includes an emergency-stop control. Safe stopping and operating procedures require engineering validation.'),
    ('Telehandler', 'Sampling Arm', 'An articulated arm illustrates assisted sample collection. Reach, sample mass and handling accuracy require dedicated testing.'),
    ('Compactor', 'Sample Carousel', 'A rotating storage concept keeps collected samples organised. Capacity and contamination controls remain subject to validation.'),
    ('Backhoe Loaders With Baskets', 'Vision Sensors', 'Visual sensing is intended to collect ore images for QualityGuard AI. Image conditions and model applicability must be checked.'),
    ('Scissors Lift', 'Sensor Mast', 'A raised mast supports the visual and scanning concept. Positioning and perception performance have not been established.'),
    ('Shotcrete Sprayers', 'Sample Handling', 'Connect each collected sample with its task, batch and position. Tool cleaning and sample integrity need a validated procedure.'),
    ('Conventional Haul Truck', 'Task Planning', 'Staff define a sampling task and review its proposed coverage before field execution.'),
    ('Concrete Mixer Truck', 'Sample Records', 'Planned records include sample identifier, time, position, batch and the corresponding laboratory result.'),
    ('Load-Haul-Dump Loader', 'Platform Link', 'The planned QualityGuard AI connection links captured images, reviewed sampling tasks and traceable sample records.'),
    ('Low-Profile Underground Truck', 'Remote Operation', 'The hardware roadmap begins with manual or remote operation before limited-area navigation is considered.'),
    ('Hydraulic Scaler', 'Image Capture', 'Capture area-labelled ore imagery under agreed conditions. Lighting, distance, dust and moisture affect comparability.'),
    ('Roof Bolters', 'Coverage Review', 'Review feature differences and sampling coverage. Visual clusters are not direct measurements of metal content.'),
    ('Face Drilling Rigs', 'Scanning Concept', 'The top-mounted scanner illustrates planned perception capability. Navigation and localisation remain to be validated.'),
]

def set_copy(tag, value):
    """Change textual content while retaining the element's animation/layout hooks."""
    if tag is None:
        return
    nodes = [n for n in tag.find_all(string=True) if n.parent.name not in ['script', 'style']]
    if nodes:
        nodes[0].replace_with(value)
        for node in nodes[1:]:
            node.replace_with('')
        return
    tag.clear()
    tag.append(value)

def replace_image(img, url=PHOTO, alt='MetriX AI Smart Sampling Rover · concept image'):
    img['src'] = url
    img['alt'] = alt
    for a in ['srcset', 'sizes']:
        img.attrs.pop(a, None)

def svg_label(svg, lines):
    """Preserve the exact SVG viewport and its animation class; change lettering only."""
    vb = svg.get('viewbox', svg.get('viewBox', '0 0 400 120'))
    _, _, w, h = map(float, vb.split())
    svg.clear()
    svg['aria-label'] = ' '.join(lines)
    svg['role'] = 'img'
    for i, line in enumerate(lines):
        t = BeautifulSoup('<text></text>', 'html.parser').find('text')
        t['x'] = str(w / 2)
        t['y'] = str(h * (i + .76) / len(lines))
        t['text-anchor'] = 'middle'
        t['fill'] = 'currentColor'
        t['font-family'] = 'Arial, sans-serif'
        t['font-weight'] = '600'
        t['font-size'] = str(min(h * .72 / len(lines), w / max(len(line) * .57, 1)))
        t.string = line
        svg.append(t)

def change_text(s):
    # Replace whole paragraphs before text nodes, retaining each paragraph's class/hooks.
    for tag in s.find_all(['p', 'h1', 'h2', 'h3', 'span', 'div']):
        if tag.find(['p','div','h1','h2','h3','svg','script','style']):
            continue
        old = norm(tag.get_text(' ', strip=True))
        if old in COPY:
            set_copy(tag, COPY[old])
            continue
        for prefix, new in PREFIX.items():
            if old.startswith(prefix):
                set_copy(tag, new)
                break
    for node in list(s.find_all(string=True)):
        if node.parent.name in ['script','style'] or node.find_parent('svg'):
            continue
        old = norm(str(node))
        if old in COPY:
            node.replace_with(COPY[old])

def machine_content(s):
    for old, new, desc in MACHINES:
        # Map every desktop/mobile equipment detail and its associated description.
        for node in list(s.find_all(string=lambda x: x and norm(x) in [old, 'Face-Drilling Rig' if old == 'Face Drilling Rigs' else old])):
            tag = node.parent
            node.replace_with(new)
            container = tag
            for parent in tag.parents:
                classes = ' '.join(parent.get('class', []))
                if any(c in classes.split() for c in ['machines-grid_item','machine-card','machine','machine-item','technology-card','machines_item']):
                    container = parent
                    break
                if parent.name == 'body':
                    break
            if container is not tag:
                for p in container.select('p'):
                    set_copy(p, desc)
    # Descriptions also occur outside the detail-card containers.
    descriptions = {
        'Precision machines used': 0, 'Essential equipment that supplies': 1,
        'Versatile material-handling': 2, 'Vibratory machines': 3, 'Modified backhoes': 4,
        'Hydraulic lifting platforms': 5, 'Specialized machines for applying': 6,
        'Heavy-duty transport vehicles': 7, 'Underground-ready mixer': 8,
        'Compact, low-profile loaders': 9, 'Purpose-built haulage': 10,
        'Specialized equipment used to remove': 11, 'Electrohydraulic machines designed': 12,
        'Electrohydraulic rigs': 13, 'booms fitted with rock drills': 13,
    }
    for p in s.select('p'):
        for prefix, i in descriptions.items():
            if norm(p.get_text()).startswith(prefix): set_copy(p, MACHINES[i][2]); break

def page_specific(s, route):
    if route == 'index.html':
        headline = s.select_one('h1')
        rows = headline.select('.is-h1-span-wrap')
        if len(rows) == 2:
            set_copy(rows[1], 'Verify Better.')
            import copy
            third = copy.copy(rows[1])
            set_copy(third, 'Recover More.')
            headline.append(third)
        for stat, (number, label) in zip(s.select('.is-stat'), [('03','AI Modules'),('01','Connected Platform'),('06','Rover Wheels'),('03','Decision Scenarios'),('01','Pilot First'),('AI','Human Reviewed')]):
            set_copy(stat.select_one('.stat_number'), number)
            set_copy(stat.select_one('.eyebrow-m'), label)
        for svg in s.select('.display svg'): svg_label(svg, ['Smart Sampling', 'Rover'])
    if route == 'technology/index.html':
        target = s.select_one('.machines-grid-wrapper')
        if target:
            demo = s.new_tag('iframe', attrs={'data-defer-src': '/rover/'}, title='Interactive MetriX Smart Sampling Rover concept')
            demo['loading'] = 'lazy'
            demo['style'] = 'display:block;width:100%;height:clamp(520px,70vh,800px);border:0;border-radius:8px;margin-bottom:32px;'
            target.insert_before(demo)
        for svg in s.select('.display svg'): svg_label(svg, ['Smart Sampling', 'Rover'])
        # Existing hero-card styling becomes the entry to the original interactive model.
        a = s.select_one('.hero-bottom .card')
        a['href'] = '/rover/'
        a.attrs.pop('pt-inner', None)
        a['target'] = '_blank'
        a['rel'] = 'noopener'
        set_copy(a.select_one('.button-sm_label'), 'Explore in 3D')
        replace_image(a.select_one('img'))
        hero = s.select_one('.hero-background img')
        if hero: replace_image(hero)
    if route == 'our-services/index.html':
        # Old project years become explicit scenario labels, not deployment dates.
        for node in list(s.find_all(string=True)):
            if norm(str(node)) in ['2018','2022','2024','2025'] and not node.find_parent(['script','style','svg']): node.replace_with('Pilot')
    if route == 'about-us/index.html':
        for col, values in zip(s.select('.date-number'), [('2','2'),('0','0'),('2','2','2','2'),('7','7','8','9')]):
            for digit, value in zip(col.select('span'), values):
                set_copy(digit, value)
        # Animated year digits keep their containers but reflect the planned roadmap.
        for el in s.select('[class*=story]'):
            if not el.find(True) and norm(el.get_text()) in ['1934','1965','1997','2002','2025']:
                set_copy(el, '2027' if norm(el.get_text()) != '2025' else '2029')
        for img in s.select('img'):
            if any(x in img.get('src','') for x in ['_ESR','_DNV','_UN','_ESR-','_UN-']): replace_image(img, ASSET+'metrix-mark.svg', 'MetriX AI · validation roadmap')
    if route == 'contact/index.html':
        form = s.select_one('form')
        form['data-metrix-brief'] = ''
        form.attrs.pop('data-wf-element-id', None)
        form.attrs.pop('data-wf-page-id', None)
        form['action'] = '/contact/'
        form.select_one('#Message')['maxlength'] = '4000'
        for label in s.select('.w-form-done'):
            label['role'] = 'status'
        # Keep the map's panel footprint; show the product instead of a false Mexico office.
        panel = s.select_one('#map')
        if panel:
            panel['id'] = 'metrix-field-concept'
            panel['style'] = f'background: url({PHOTO}) center / cover no-repeat;'
            panel['role'] = 'img'
            panel['aria-label'] = 'MetriX AI rover concept; initial cooperation focus is Guangxi'
    if route == 'join-the-team/index.html':
        for node in list(s.find_all(string=True)):
            if re.fullmatch(r'(September|October) \d+, 2025', norm(str(node))): node.replace_with('Proposed pilot')
        for svg in s.select('svg'):
            if any(x in svg.get('aria-label','').lower() for x in ['gender','women']): svg_label(svg,['Data + Review'])
    if route.startswith('blog/') and route != 'blog/index.html':
        rich = s.select_one('.w-richtext')
        if rich:
            key = 0 if 'safety-first' in route else 1 if 'open-pit' in route else 2
            articles = [
                [('h2','Sampling starts with coverage'),('p','QualityGuard AI analyses visual feature differences across an ore pile and helps teams review where samples are collected. The goal is stronger evidence for quality decisions.'),('h2','What the module uses'),('p','Area-labelled images, batch information, existing sampling points and matched laboratory results provide the input. Light, distance, dust and moisture must be controlled or documented.'),('h2','What it recommends'),('p','Feature maps, sampling locations, suggested quantities and additional coverage help staff review a sampling plan within the agreed budget and access constraints.'),('h2','What still needs testing'),('p','Visual clusters do not certify metal grade. Surface images cannot fully describe internal layers. Appropriate sampling methods, laboratory testing and professional review remain essential.'),('h2','The field extension'),('p','The Smart Sampling Rover is a planned link between reviewed tasks, image collection and traceable samples. Hardware and operating conditions require separate validation.')],
                [('h2','Match equipment to the task'),('p','MineFit AI considers payload, current position, equipment availability and road restrictions before comparing feasible assignments.'),('h2','Compare routes consistently'),('p','Route analysis combines distance, slope, energy and congestion on a consistent scale. Estimated time and cost should show the input data and assumptions used.'),('h2','Respond to scenario changes'),('p','A road closure, unavailable vehicle or revised task can trigger a new recommendation when the updated information is supplied. Offline analysis is not described as live dispatch.'),('h2','Validate against a baseline'),('p','A pilot compares the current rules and module recommendations using identical tasks and fleet conditions. Route distance, task time, waiting time and constraint violations can inform acceptance.'),('h2','Keep the operator in control'),('p','The first stage focuses on offline recommendations and simulation. Production system integration is a later scope; staff review recommendations before use.')],
                [('h2','Screen secondary resources'),('p','CircularMine AI compares potential recovery options for tailings and suitable industrial by-products. Use material-specific measurements and applicable recovery trial data.'),('h2','Connect quantity, grade and recovery'),('p','Recoverable element quantity equals dry material quantity multiplied by element mass fraction and process recovery. Units must be consistent.'),('h2','Compare revenue and operating costs'),('p','Estimated sales revenue uses saleable quantity, the relevant product price and any payable factor. Subtract processing, energy, transport, environmental treatment and other relevant operating costs.'),('h2','Test the assumptions'),('p','Sensitivity analysis shows how price, recovery and cost changes affect the ranking of candidate pathways. Mark assumptions clearly and prioritise additional tests where evidence is weak.'),('h2','Know the assessment boundary'),('p','Estimated net operating value supports screening. Investment feasibility also needs capital, schedule, tax, financing and cash-flow analysis. A high element content alone does not establish profitability.')]
            ]
            rich.clear()
            for tag, value in articles[key]:
                el=s.new_tag(tag);el.string=value;rich.append(el)
    if route == 'notice-of-privacy/index.html':
        # This is a product/data scope page, not a fabricated legal policy for a different company.
        paragraphs = s.select('.p-notice')
        scope = [
            'MetriX AI · Product and data scope. This local product website presents a prototype and proof-of-concept project. Proposed services and deployment options require validation and an agreed delivery scope.',
            'MineFit AI supports equipment matching and route comparison; initial validation uses offline or simulated scenarios.',
            'QualityGuard AI supports feature-based sampling analysis. Visual differences are not certified measurements of metal grade.',
            'CircularMine AI supports early resource and pathway assessment using measured data and stated assumptions.',
            'The Smart Sampling Rover is a hardware concept. Images and the interactive model illustrate the design and are not evidence of manufacture, deployment or certified performance.',
            'The pilot brief form generates a text file locally in your browser. It does not send your name, email or message to MetriX AI or the previous website owner.',
            'Pilot data access, result ownership, permitted uses, retention and export should be agreed with the relevant parties before data is shared.',
            'Use of customer data for model training or cross-customer research requires explicit agreement on purpose and scope.',
            'Enterprise permissions, audit records, backup and deployment options are proposed productisation requirements. Their delivery depends on the agreed project scope.',
            'Model outputs should identify sources, units, parameter versions and applicability limits. Important decisions remain subject to professional review.',
            'For the complete project description and proposed services, download the supplied Chinese product introduction from this website.',
        ]
        for i,p in enumerate(paragraphs):
            set_copy(p, scope[i] if i < len(scope) else 'Scope and acceptance criteria are established for each proposed pilot before wider deployment.')
        # Remove obsolete legal list text not contained in the original paragraph elements.
        for el in s.select('li'):
            if el.select('.p-notice') or el.find_parent('ul', class_=['links', 'footer-links']): continue
            set_copy(el, 'Data use and delivery scope are agreed for each pilot.')

def adapt(source, route):
    s = BeautifulSoup(source, 'html.parser')
    machine_content(s)
    change_text(s)
    page_specific(s, route)
    # Existing cards keep their dimensions and movement; only the visual subject changes.
    for img in s.select('.is-machine, .machines-grid_img, .machines-grid_image, .machines-grid_infos img'):
        replace_image(img)
    for img in s.select('img'):
        if any(x in img.get('src','') for x in ['technology-min','home_01','home_02']): replace_image(img)
    # Replace partner endorsements with audience/module labels in the same moving logo slots.
    labels = ['MineFit AI','QualityGuard AI','CircularMine AI','Smart Rover'] if route == 'technology/index.html' else ['Mining Operators','Testing Teams','Resource Recovery','Industry Partners']
    for i, svg in enumerate(s.select('.logos-slider_logo, .partners_logo, .partner-logo')):
        if svg.name == 'svg': svg_label(svg, [labels[i % len(labels)]])
        elif svg.name == 'img': replace_image(svg, ASSET+'metrix-mark.svg','MetriX AI')
    # Remove inherited organization/review/job schema and replace with supported identity.
    for schema in s.select('script[type="application/ld+json"]'): schema.decompose()
    schema=s.new_tag('script',type='application/ld+json')
    schema.string=json.dumps({'@context':'https://schema.org','@type':'Organization','name':'MetriX AI','description':'Prototype decision-support platform for mining operations, sampling and secondary resource assessment.','slogan':'Mine Smarter. Verify Better. Recover More.'})
    s.head.append(schema)
    title={'index.html':'MetriX AI | Mine Smarter. Verify Better. Recover More.', 'our-services/index.html':'AI Solutions | MetriX AI', 'technology/index.html':'Smart Sampling Rover | MetriX AI', 'about-us/index.html':'About the Project | MetriX AI', 'safety/index.html':'Validation & Human Review | MetriX AI', 'contact/index.html':'Prepare a Pilot | MetriX AI', 'join-the-team/index.html':'Pilot Partners | MetriX AI', 'blog/index.html':'Product Insights | MetriX AI', 'notice-of-privacy/index.html':'Data & Product Scope | MetriX AI'}.get(route, (s.h1.get_text(' ',strip=True) if s.h1 else 'Product Guide')+' | MetriX AI')
    s.title.string=title
    for meta in s.select('meta'):
        key=meta.get('name',meta.get('property',''))
        if key in ['description','og:description','twitter:description']:meta['content']='MetriX AI connects equipment and route optimisation, sampling support and secondary resource value assessment. Explore our prototype platform and smart sampling rover concept.'
        elif key in ['og:title','twitter:title']:meta['content']=title
        elif key in ['og:image','twitter:image']:meta['content']=PHOTO
        elif key in ['og:site_name']:meta['content']='MetriX AI'
        elif key in ['og:url','twitter:url']:meta['content']='/' if route=='index.html' else '/'+route.removesuffix('index.html')
    for link in s.select('link[rel="alternate"]'):link.decompose()
    for a in s.select('a[href]'):
        href=a['href']
        if href.startswith('mailto:') or 'info@cominvi' in href:
            a['href']=DOC;a['download']='MetriX-AI-Product-Introduction-CN.docx';a.attrs.pop('pt-inner',None)
        elif href.startswith('tel:'):
            a['href']='/contact/'
        elif any(x in href for x in ['facebook.com','instagram.com','linkedin.com','holographik','youtube.com','wa.me']):
            a['href']='/contact/';a['aria-label']='Discuss a MetriX AI pilot'
        elif href.startswith('/es'):
            a['href']=DOC;a['download']='MetriX-AI-Product-Introduction-CN.docx';a.attrs.pop('pt-inner',None)
            for node in list(a.find_all(string=True)):
                if norm(str(node)) in ['Es','ES','Español']:node.replace_with('Guide')
        if a.get('href')==DOC:a.attrs.pop('target',None)
    for x in s.select('[aria-label]'):
        old=x['aria-label']
        if old in COPY:x['aria-label']=COPY[old]
        elif 'cominvi' in old.lower():x['aria-label']='MetriX AI'
    for svg in s.select('svg'):
        if norm(svg.get_text()) == 'Map of our projects in Mexico':
            svg_label(svg, ['Potential pilot applications'])
    for text in s.select('svg text'):
        if norm(text.get_text()) == 'MetriX':
            text.string = 'MetriX AI'
    for link in s.select('link[rel="canonical"]'):link['href']='/' if route=='index.html' else '/'+route.removesuffix('index.html')
    js=s.new_tag('script', src=ASSET+'product.js');js['defer']='';s.head.append(js)
    update_media(s)
    return str(s)

def main():
    shutil.copy2(r'C:\Users\User\Downloads\MetriX_AI_Product_Introduction_CN.docx', SITE / DOC.lstrip('/'))
    (SITE/ASSET.lstrip('/')/'metrix-mark.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120"><text x="200" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="72" font-weight="600" fill="#151515">MetriX AI</text></svg>','utf-8')
    pages=[]
    for source in BEFORE.rglob('*.html'):
        route=source.relative_to(BEFORE).as_posix()
        if route.startswith('es/'):continue
        output=adapt(source.read_text('utf-8'),route)
        (SITE/route).write_text(output,'utf-8')
        pages.append(route)
        # Retained old locale URLs resolve to the same supported product content.
        spanish=SITE/'es'/route
        if spanish.exists():spanish.write_text(output,'utf-8')
    print(json.dumps({'adapted_pages':pages},indent=2))

if __name__=='__main__':main()
