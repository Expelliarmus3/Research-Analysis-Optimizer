from app import app, db, User, Internship

with app.app_context():
    db.create_all()
    
    # 1. Create a Default Professor
    if not User.query.filter_by(email="prof@mit.edu").first():
        prof = User(email="prof@mit.edu", password="123", role="Professor", full_name="Dr. Elara Vance")
        db.session.add(prof)
        db.session.commit()
        print("✅ Professor Account Created (Email: prof@mit.edu / Pass: 123)")

    # 2. Add the Trending Research Papers (From your screenshot)
    # We use the Internship table to store these as "Opportunities"
    prof_id = User.query.filter_by(email="prof@mit.edu").first().id
    
    papers = [
        {
            "title": "Attention Is All You Need",
            "domain": "Deep Learning",
            "type": "Remote",
            "desc": "The seminal paper introducing the Transformer architecture, the foundation of modern LLMs like GPT."
        },
        {
            "title": "YOLOv8: Real-Time Detection",
            "domain": "Computer Vision",
            "type": "Onsite",
            "desc": "State-of-the-art real-time object detection model offering SOTA performance on COCO dataset."
        },
        {
            "title": "BERT: Pre-training of Deep Transformers",
            "domain": "NLP",
            "type": "Hybrid",
            "desc": "Bidirectional Encoder Representations from Transformers (BERT) revolutionized NLP tasks."
        },
        {
            "title": "Llama 2: Open Foundation Models",
            "domain": "Generative AI",
            "type": "Remote",
            "desc": "A collection of open-source pretrained and fine-tuned large language models (LLMs)."
        }
    ]

    for p in papers:
        if not Internship.query.filter_by(title=p['title']).first():
            new_paper = Internship(
                title=p['title'],
                domain=p['domain'],
                type=p['type'],
                description=p['desc'],
                required_skills="Python, PyTorch, Research",
                user_id=prof_id
            )
            db.session.add(new_paper)
    
    db.session.commit()
    print("✅ Trending Research Papers Added!")