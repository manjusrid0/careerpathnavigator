from app import db, Career, app

with app.app_context():
    # Clear old data
    db.drop_all()
    db.create_all()

    # Sample Careers
    careers = [
        Career(
            title="Data Scientist",
            description="Data Scientists analyze complex datasets to uncover patterns, "
                        "build predictive models, and help organizations make data-driven decisions."
        ),
        Career(
            title="Web Developer",
            description="Web Developers design and build websites and web applications, "
                        "working with frontend and backend technologies."
        ),
        Career(
            title="AI Engineer",
            description="AI Engineers design and deploy artificial intelligence systems, "
                        "including machine learning and natural language processing models."
        ),
        Career(
            title="Cybersecurity Analyst",
            description="Cybersecurity Analysts protect systems and networks from cyber threats "
                        "by monitoring, detecting, and responding to attacks."
        ),
        Career(
            title="Cloud Architect",
            description="Cloud Architects design and manage scalable, reliable, and secure cloud solutions "
                        "for businesses using platforms like AWS, Azure, or Google Cloud."
        ),
    ]

    # Insert into database
    db.session.bulk_save_objects(careers)
    db.session.commit()

    print("✅ Careers seeded successfully!")
