from app import create_app, db
from app.models import User, Question, Test, UserProgress, TestResult
import click

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Question': Question, 'Test': Test, 'UserProgress': UserProgress, 'TestResult': TestResult}

@app.cli.command("seed-db")
def seed_db():
    """Seeds the database with sample questions and tests."""
    # Clear existing data to prevent duplicates on re-seeding
    db.session.query(UserProgress).delete()
    db.session.query(TestResult).delete()
    db.session.query(Test).delete()
    db.session.query(Question).delete()
    db.session.commit()

    # Define questions first
    questions_data = [
        # Chem/Phys Questions
        {
            "section": "Chem/Phys", "topic": "Thermodynamics", "difficulty": "Easy",
            "question_text": "What is the first law of thermodynamics?",
            "option_a": "Energy cannot be created or destroyed.",
            "option_b": "The entropy of the universe is always increasing.",
            "option_c": "Absolute zero is unattainable.",
            "option_d": "For every action, there is an equal and opposite reaction.",
            "correct_answer": "A",
            "explanation": "The first law of thermodynamics, also known as the law of conservation of energy, states that energy cannot be created or destroyed in an isolated system."
        },
        {
            "section": "Chem/Phys", "topic": "Fluid Dynamics", "difficulty": "Medium",
            "question_text": "According to Bernoulli's principle, what happens to the pressure of a fluid as its velocity increases?",
            "option_a": "It increases", "option_b": "It decreases", "option_c": "It remains constant", "option_d": "It fluctuates randomly",
            "correct_answer": "B",
            "explanation": "Bernoulli's principle states that an increase in the speed of a fluid occurs simultaneously with a decrease in static pressure or a decrease in the fluid's potential energy."
        },
        {
            "section": "Chem/Phys", "topic": "Optics", "difficulty": "Medium",
            "question_text": "A converging lens has a focal length of 10 cm. An object is placed 30 cm from the lens. Where will the image be formed?",
            "option_a": "15 cm on the same side as the object", "option_b": "15 cm on the opposite side of the object",
            "option_c": "30 cm on the same side as the object", "option_d": "30 cm on the opposite side of the object",
            "correct_answer": "B",
            "explanation": "Using the thin lens equation (1/f = 1/do + 1/di), where f = 10 cm and do = 30 cm, we get 1/10 = 1/30 + 1/di. Solving for di gives di = 15 cm. Since di is positive, the image is formed on the opposite side of the lens."
        },
        {
            "section": "Chem/Phys", "topic": "Electrochemistry", "difficulty": "Hard",
            "question_text": "In a galvanic cell, which electrode is where oxidation occurs?",
            "option_a": "Cathode", "option_b": "Anode", "option_c": "Salt bridge", "option_d": "External circuit",
            "correct_answer": "B",
            "explanation": "In both galvanic (voltaic) and electrolytic cells, oxidation always occurs at the anode."
        },
        {
            "section": "Chem/Phys", "topic": "Kinematics", "difficulty": "Easy",
            "question_text": "A car accelerates from rest to 20 m/s in 5 seconds. What is its average acceleration?",
            "option_a": "2 m/s^2", "option_b": "4 m/s^2", "option_c": "5 m/s^2", "option_d": "10 m/s^2",
            "correct_answer": "B",
            "explanation": "Average acceleration = change in velocity / time = (20 m/s - 0 m/s) / 5 s = 4 m/s^2."
        },
        {
            "section": "Chem/Phys", "topic": "Work and Energy", "difficulty": "Medium",
            "question_text": "How much work is done when a 10 kg object is lifted vertically by 5 meters? (g = 9.8 m/s^2)",
            "option_a": "49 J", "option_b": "98 J", "option_c": "490 J", "option_d": "980 J",
            "correct_answer": "C",
            "explanation": "Work done = Force x Distance = (mass x gravity) x distance = (10 kg x 9.8 m/s^2) x 5 m = 490 J."
        },
        {
            "section": "Chem/Phys", "topic": "Acids and Bases", "difficulty": "Hard",
            "question_text": "What is the pH of a 0.01 M solution of HCl?",
            "option_a": "1", "option_b": "2", "option_c": "7", "option_d": "12",
            "correct_answer": "B",
            "explanation": "HCl is a strong acid, so it fully dissociates. [H+] = 0.01 M. pH = -log[H+] = -log(0.01) = 2."
        },

        # Bio/Biochem Questions
        {
            "section": "Bio/Biochem", "topic": "Genetics", "difficulty": "Medium",
            "question_text": "What is the central dogma of molecular biology?",
            "option_a": "DNA -> RNA -> Protein", "option_b": "RNA -> DNA -> Protein",
            "option_c": "Protein -> RNA -> DNA", "option_d": "DNA -> Protein -> RNA",
            "correct_answer": "A",
            "explanation": "The central dogma of molecular biology describes the two-step process, transcription and translation, by which the information in genes flows into proteins: DNA -> RNA -> protein."
        },
        {
            "section": "Bio/Biochem", "topic": "Enzymes", "difficulty": "Hard",
            "question_text": "Which type of enzyme catalyzes the transfer of a phosphate group from ATP to a substrate?",
            "option_a": "Hydrolase", "option_b": "Isomerase", "option_c": "Kinase", "option_d": "Ligase",
            "correct_answer": "C",
            "explanation": "Kinases are enzymes that catalyze the transfer of phosphate groups from high-energy donor molecules (like ATP) to specific substrates."
        },
        {
            "section": "Bio/Biochem", "topic": "Cell Biology", "difficulty": "Easy",
            "question_text": "Which organelle is responsible for generating most of the ATP in eukaryotic cells?",
            "option_a": "Nucleus", "option_b": "Mitochondria", "option_c": "Endoplasmic Reticulum", "option_d": "Golgi Apparatus",
            "correct_answer": "B",
            "explanation": "Mitochondria are often referred to as the 'powerhouses' of the cell because they generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."
        },
        {
            "section": "Bio/Biochem", "topic": "Physiology", "difficulty": "Medium",
            "question_text": "Which of the following hormones is primarily responsible for regulating blood glucose levels by promoting glucose uptake by cells?",
            "option_a": "Glucagon", "option_b": "Insulin", "option_c": "Cortisol", "option_d": "Epinephrine",
            "correct_answer": "B",
            "explanation": "Insulin is a hormone produced by the pancreas that plays a key role in regulating blood glucose levels. It facilitates the uptake of glucose from the blood into cells for energy or storage."
        },
        {
            "section": "Bio/Biochem", "topic": "DNA Replication", "difficulty": "Medium",
            "question_text": "Which enzyme is responsible for unwinding the DNA double helix during replication?",
            "option_a": "DNA ligase", "option_b": "DNA polymerase", "option_c": "Helicase", "option_d": "Primase",
            "correct_answer": "C",
            "explanation": "Helicase unwinds the DNA double helix by breaking the hydrogen bonds between complementary base pairs."
        },
        {
            "section": "Bio/Biochem", "topic": "Protein Structure", "difficulty": "Hard",
            "question_text": "What type of bond is primarily responsible for the secondary structure of proteins?",
            "option_a": "Disulfide bonds", "option_b": "Ionic bonds", "option_c": "Hydrogen bonds", "option_d": "Peptide bonds",
            "correct_answer": "C",
            "explanation": "Hydrogen bonds between the carboxyl oxygen of one amino acid and the amino hydrogen of another are responsible for the formation of alpha-helices and beta-pleated sheets, which constitute the secondary structure of proteins."
        },
        {
            "section": "Bio/Biochem", "topic": "Metabolism", "difficulty": "Easy",
            "question_text": "What is the end product of glycolysis in the presence of oxygen?",
            "option_a": "Lactate", "option_b": "Pyruvate", "option_c": "Acetyl-CoA", "option_d": "Glucose",
            "correct_answer": "B",
            "explanation": "In aerobic conditions, glycolysis produces two molecules of pyruvate from one molecule of glucose."
        },

        # Psych/Soc Questions
        {
            "section": "Psych/Soc", "topic": "Social Behavior", "difficulty": "Easy",
            "question_text": "What is the bystander effect?",
            "option_a": "People are more likely to help in an emergency when others are present.",
            "option_b": "People are less likely to help in an emergency when others are present.",
            "option_c": "People are more likely to conform to group norms.",
            "option_d": "People are less likely to conform to group norms.",
            "correct_answer": "B",
            "explanation": "The bystander effect is a social psychological phenomenon in which individuals are less likely to offer help to a victim when other people are present."
        },
        {
            "section": "Psych/Soc", "topic": "Cognition", "difficulty": "Medium",
            "question_text": "What is the difference between proactive and retroactive interference?",
            "option_a": "Proactive interference is when new information interferes with old, retroactive is when old interferes with new.",
            "option_b": "Proactive interference is when old information interferes with new, retroactive is when new interferes with old.",
            "option_c": "Both refer to the same phenomenon.",
            "option_d": "They are types of memory consolidation.",
            "correct_answer": "B",
            "explanation": "Proactive interference occurs when old information hinders the recall of newly learned information. Retroactive interference occurs when new information hinders the recall of old information."
        },
        {
            "section": "Psych/Soc", "topic": "Developmental Psychology", "difficulty": "Hard",
            "question_text": "According to Piaget's theory of cognitive development, during which stage do children begin to think logically about concrete events?",
            "option_a": "Sensorimotor", "option_b": "Preoperational", "option_c": "Concrete Operational", "option_d": "Formal Operational",
            "correct_answer": "C",
            "explanation": "The Concrete Operational Stage (ages 7 to 11) is characterized by the development of organized and rational thinking. Children at this stage are capable of logical thought about concrete events."
        },
        {
            "section": "Psych/Soc", "topic": "Learning", "difficulty": "Medium",
            "question_text": "In classical conditioning, what is an unconditioned stimulus?",
            "option_a": "A neutral stimulus that becomes associated with a response.",
            "option_b": "A stimulus that naturally and automatically triggers a response.",
            "option_c": "A learned response to a previously neutral stimulus.",
            "option_d": "A stimulus that is presented after a behavior to increase its likelihood.",
            "correct_answer": "B",
            "explanation": "An unconditioned stimulus (UCS) is a stimulus that naturally and automatically triggers a response without any prior learning."
        },
        {
            "section": "Psych/Soc", "topic": "Emotion", "difficulty": "Hard",
            "question_text": "Which theory of emotion suggests that physiological arousal and emotional experience occur simultaneously?",
            "option_a": "James-Lange theory", "option_b": "Cannon-Bard theory", "option_c": "Schachter-Singer two-factor theory", "option_d": "Lazarus cognitive-mediational theory",
            "correct_answer": "B",
            "explanation": "The Cannon-Bard theory of emotion states that physiological arousal and emotional experience occur at the same time, but independently."
        },
        {
            "section": "Psych/Soc", "topic": "Memory", "difficulty": "Easy",
            "question_text": "What is the capacity of short-term memory?",
            "option_a": "Unlimited", "option_b": "Very limited, typically 7 +/- 2 items",
            "option_c": "Depends on the individual's intelligence", "option_d": "Only visual information",
            "correct_answer": "B",
            "explanation": "George Miller's research suggests that the capacity of short-term memory is about seven plus or minus two items."
        },

        # CARS Questions
        {
            "section": "CARS", "topic": "Reasoning", "difficulty": "Hard",
            "question_text": "Which of the following best describes the author's tone in the passage?",
            "option_a": "Sarcastic", "option_b": "Objective", "option_c": "Condescending", "option_d": "Enthusiastic",
            "correct_answer": "B",
            "explanation": "Without the passage, it's hard to say, but 'objective' is a common correct answer for CARS passages that present information without strong bias.",
            "passage_text": "The following passage discusses the impact of technology on modern society. \n\nTechnology has rapidly transformed various aspects of human life, from communication to commerce. While it offers unprecedented convenience and access to information, concerns about its long-term effects on social interaction and mental well-being are growing. The constant connectivity fostered by smartphones and social media platforms, for instance, has been linked to increased feelings of isolation and anxiety in some individuals. Moreover, the proliferation of misinformation and the erosion of privacy in the digital age present significant challenges that society must address."
        },
        {
            "section": "CARS", "topic": "Philosophy", "difficulty": "Medium",
            "question_text": "Based on the passage, what is the author's primary argument regarding the role of art in society?",
            "option_a": "Art serves primarily as a form of entertainment.",
            "option_b": "Art is essential for social commentary and change.",
            "option_c": "Art's value is purely aesthetic.",
            "option_d": "Art has no significant impact on societal development.",
            "correct_answer": "B",
            "explanation": "The passage emphasizes art's capacity to reflect and influence societal values, suggesting its role extends beyond mere entertainment or aesthetic appeal.",
            "passage_text": "Art, throughout history, has been more than just a decorative element; it has been a powerful mirror reflecting the prevailing social, political, and cultural landscapes. From ancient cave paintings depicting daily life to Renaissance masterpieces challenging religious dogma, art has consistently served as a medium for expression, critique, and transformation. In contemporary society, artists continue to use their craft to highlight injustices, provoke thought, and inspire collective action, demonstrating art's enduring capacity to shape public discourse and drive societal change."
        },
        {
            "section": "CARS", "topic": "Literary Analysis", "difficulty": "Medium",
            "question_text": "The author's use of vivid imagery in the second paragraph primarily serves to:",
            "option_a": "Distract the reader from the main argument.",
            "option_b": "Enhance the emotional impact of the narrative.",
            "option_c": "Provide a factual account of events.",
            "option_d": "Introduce a counter-argument.",
            "correct_answer": "B",
            "explanation": "Vivid imagery often appeals to the senses and can evoke strong emotions, thereby enhancing the emotional impact of a narrative."
        },
        {
            "section": "CARS", "topic": "Argument Analysis", "difficulty": "Easy",
            "question_text": "The author's main purpose in this passage is to:",
            "option_a": "Persuade the reader to adopt a particular viewpoint.",
            "option_b": "Inform the reader about a historical event.",
            "option_c": "Entertain the reader with a fictional story.",
            "option_d": "Critique a scientific theory.",
            "correct_answer": "B",
            "explanation": "Identifying the main purpose requires understanding the overall aim of the passage. If it presents facts and details about a past event, informing is the primary purpose."
        },
        {
            "section": "CARS", "topic": "Social Sciences", "difficulty": "Hard",
            "question_text": "Which of the following best summarizes the author's critique of modern consumerism?",
            "option_a": "It promotes economic growth and individual freedom.",
            "option_b": "It leads to environmental degradation and social alienation.",
            "option_c": "It encourages innovation and technological advancement.",
            "option_d": "It is a natural and inevitable outcome of human progress.",
            "correct_answer": "B",
            "explanation": "The passage details how consumerism, while seemingly beneficial, has detrimental effects on both the environment and human social connections, leading to a sense of detachment.",
            "passage_text": "Modern consumerism, often lauded as the engine of economic prosperity, presents a complex paradox. While it undeniably fuels industrial output and provides a vast array of goods and services, its relentless pursuit of material acquisition carries significant hidden costs. The ecological footprint of mass production and disposable goods strains planetary resources, contributing to pollution and climate change. Furthermore, the emphasis on individual consumption can erode community bonds, fostering a sense of isolation and competition rather than collective well-being. Critics argue that this insatiable drive for more, often fueled by pervasive advertising, distracts from deeper human needs and sustainable societal development."
        },
        {
            "section": "CARS", "topic": "Humanities", "difficulty": "Medium",
            "question_text": "The author's discussion of classical literature primarily serves to:",
            "option_a": "Illustrate the timeless nature of human emotions.",
            "option_b": "Critique the limitations of ancient storytelling.",
            "option_c": "Compare ancient and modern literary techniques.",
            "option_d": "Argue for the superiority of past artistic forms.",
            "correct_answer": "A",
            "explanation": "The passage uses examples from classical literature to demonstrate how fundamental human emotions and experiences, such as love, loss, and ambition, have been consistently explored across different eras, highlighting their enduring relevance.",
            "passage_text": "From the epic poems of Homer to the tragedies of Shakespeare, classical literature offers a profound window into the human condition. These works, though separated by centuries and cultural contexts, resonate with contemporary readers precisely because they grapple with universal themes: the complexities of love, the pangs of betrayal, the pursuit of justice, and the inevitability of fate. The characters, despite their ancient garb, embody emotions and dilemmas that remain strikingly familiar. This enduring appeal suggests that while the external trappings of society may change, the core emotional landscape of humanity remains remarkably constant, a testament to the power of these narratives to transcend time."
        },
        {
            "section": "CARS", "topic": "Ethics",
            "difficulty": "Hard",
            "question_text": "Which of the following principles would the author most likely endorse regarding the ethical implications of artificial intelligence?",
            "option_a": "Prioritizing technological advancement above all else.",
            "option_b": "Ensuring AI development aligns with human values and societal well-being.",
            "option_c": "Limiting AI research to prevent unforeseen risks.",
            "option_d": "Allowing AI to evolve autonomously without human intervention.",
            "correct_answer": "B",
            "explanation": "The passage emphasizes the need for careful consideration of AI's impact on society and the importance of guiding its development to serve humanity's best interests, aligning with the principle of ethical alignment.",
            "passage_text": "The rapid proliferation of artificial intelligence (AI) presents humanity with both unprecedented opportunities and profound ethical challenges. As AI systems become increasingly sophisticated, capable of autonomous decision-making and learning, questions arise regarding accountability, bias, and the potential for unintended consequences. While the promise of AI in fields like medicine and scientific discovery is immense, a purely utilitarian approach that prioritizes efficiency over human values risks creating systems that exacerbate existing inequalities or undermine fundamental rights. Therefore, a robust ethical framework is paramount, one that ensures AI development is guided by principles of fairness, transparency, and a deep commitment to human flourishing."
        },
        {
            "section": "CARS", "topic": "Art History",
            "difficulty": "Medium",
            "question_text": "The author suggests that the shift from classical to modern art was primarily driven by:",
            "option_a": "A rejection of traditional artistic techniques.",
            "option_b": "The influence of new scientific discoveries.",
            "option_c": "Changing societal values and perspectives.",
            "option_d": "The desire for greater commercial success.",
            "correct_answer": "C",
            "explanation": "The passage highlights how societal shifts, such as industrialization and new philosophical movements, led artists to explore different forms of expression that better reflected the changing human experience, rather than solely technical or commercial motivations.",
            "passage_text": "The evolution of art from classical forms to modern expressions is not merely a story of changing aesthetics, but a profound reflection of shifting societal landscapes. Classical art, with its emphasis on idealized forms and narrative clarity, often served to reinforce established hierarchies and religious doctrines. However, as societies underwent industrialization, urbanization, and intellectual revolutions, artists began to question traditional representations. The rise of individualism, new scientific understandings, and a growing awareness of psychological complexities spurred a desire for art that was more introspective, fragmented, and challenging. This transition was less about a sudden rejection of the past and more about artists seeking new visual languages to articulate the complexities of a rapidly transforming world."
        }
    ]

    # Add questions to the session and commit to get IDs
    for q_data in questions_data:
        q = Question(**q_data)
        db.session.add(q)
    db.session.commit()
    print(f"Seeded {len(questions_data)} questions.")

    # Add a default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('adminpass')
        db.session.add(admin_user)

    db.session.commit()

    # Seed Tests
    # Retrieve all questions from the database to ensure they have IDs
    q_all = Question.query.all()
    q_map = {q.question_text: q for q in q_all} # Map questions by text for easy lookup

    # Example Test 1: Diagnostic Test (Mixed Sections)
    test1_questions_texts = [
        "What is the first law of thermodynamics?",
        "What is the central dogma of molecular biology?",
        "What is the bystander effect?",
        "Which of the following best describes the author's tone in the passage?",
        "According to Bernoulli's principle, what happens to the pressure of a fluid as its velocity increases?",
        "Which type of enzyme catalyzes the transfer of a phosphate group from ATP to a substrate?",
        "Based on the passage, what is the author's primary argument regarding the role of art in society?",
        "A converging lens has a focal length of 10 cm. An object is placed 30 cm from the lens. Where will the image be formed?",
        "Which organelle is responsible for generating most of the ATP in eukaryotic cells?",
        "What is the difference between proactive and retroactive interference?"
    ]
    test1_questions = [q_map[text] for text in test1_questions_texts if text in q_map]

    if len(test1_questions) == len(test1_questions_texts):
        test1 = Test(
            name="Diagnostic Test 1",
            description="A comprehensive diagnostic test covering all MCAT sections.",
            duration_minutes=60,
            questions=test1_questions
        )
        db.session.add(test1)
    else:
        print("Warning: Not all questions for Diagnostic Test 1 were found. Test not created.")

    # Example Test 2: CARS Mini-Test
    cars_questions_texts = [
        "Which of the following best describes the author's tone in the passage?",
        "Based on the passage, what is the author's primary argument regarding the role of art in society?",
        "The author's use of vivid imagery in the second paragraph primarily serves to:",
        "The author's main purpose in this passage is to:",
        "Which of the following best summarizes the author's critique of modern consumerism?"
    ]
    cars_questions_for_test = [q_map[text] for text in cars_questions_texts if text in q_map]

    if len(cars_questions_for_test) == len(cars_questions_texts):
        test2 = Test(
            name="CARS Mini-Test 1",
            description="A short practice test focusing on Critical Analysis and Reasoning Skills.",
            duration_minutes=20,
            questions=cars_questions_for_test
        )
        db.session.add(test2)
    else:
        print("Warning: Not all CARS questions for CARS Mini-Test 1 were found. Test not created.")

    # Example Test 3: Bio/Biochem Section Test
    bio_biochem_questions_texts = [
        "What is the central dogma of molecular biology?",
        "Which type of enzyme catalyzes the transfer of a phosphate group from ATP to a substrate?",
        "Which organelle is responsible for generating most of the ATP in eukaryotic cells?",
        "Which of the following hormones is primarily responsible for regulating blood glucose levels by promoting glucose uptake by cells?",
        "Which enzyme is responsible for unwinding the DNA double helix during replication?",
        "What type of bond is primarily responsible for the secondary structure of proteins?",
        "What is the end product of glycolysis in the presence of oxygen?"
    ]
    bio_biochem_questions_for_test = [q_map[text] for text in bio_biochem_questions_texts if text in q_map]

    if len(bio_biochem_questions_for_test) == len(bio_biochem_questions_texts):
        test3 = Test(
            name="Bio/Biochem Section Test 1",
            description="A practice test focused on Biological and Biochemical Foundations.",
            duration_minutes=35,
            questions=bio_biochem_questions_for_test
        )
        db.session.add(test3)
    else:
        print("Warning: Not all Bio/Biochem questions for Bio/Biochem Section Test 1 were found. Test not created.")

    db.session.commit()
    print("Tests seeded successfully.")
