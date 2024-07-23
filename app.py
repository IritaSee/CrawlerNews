from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from CrawlerGeneral import crawlerGeneral
from CrawlerTopik import crawlerWithTopik

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost/pukulenam?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model ORM
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_fake = db.Column(db.Integer, default=0)
    media_bias = db.Column(db.String(30), nullable=False)
    topik = db.Column(db.String(30), nullable=False)


# Buat database dan tabel
with app.app_context():
    db.create_all()

@app.route('/api/crawler/general', methods=['GET'])
def run_crawler_general():
    result = crawlerGeneral()
    try:
        # Mengosongkan tabel sebelum menambahkan data baru
        db.session.query(News).filter(News.topik == 'general').delete()
        db.session.commit()
        
        # Menambahkan data hasil crawler ke tabel
        for item in result:
            news = News(
                title=item['title'],
                link=item['link'],
                image=item['image'],
                content=item['content'],
                is_fake=item.get('is_fake', 0),
                media_bias=item['media_bias'],
                topik = 'general'
            )
            db.session.add(news)
        db.session.commit()
        return jsonify({'message': 'News updated successfully from general crawler'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/crawler/topik', methods=['POST'])
def run_crawler_topik():
    data = request.get_json()
    topik = data.get('topik')
    result = crawlerWithTopik(topik)
    try:
        # Mengosongkan tabel sebelum menambahkan data baru
        db.session.query(News).filter(News.topik == topik).delete()
        db.session.commit()
        
        # Menambahkan data hasil crawler ke tabel
        for item in result:
            news = News(
                title=item['title'],
                link=item['link'],
                image=item['image'],
                content=item['content'],
                is_fake=item.get('is_fake', 0),
                media_bias=item['media_bias'],
                topik = topik
            )
            db.session.add(news)
        db.session.commit()
        return jsonify({'message': 'News updated successfully from topic crawler'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    news = News.query.all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'link': n.link,
        'image': n.image,
        'content': n.content,
        'date': n.date.isoformat(),
        'is_fake': n.is_fake,
        'media_bias': n.media_bias
    } for n in news])

@app.route('/api/news', methods=['POST'])
def add_news():
    data = request.get_json()
    try: 
        db.session.query(News).delete()
        db.session.commit()
        for item in data:
            news = News(
                title=item['title'],
                link=item['link'],
                image=item['image'],
                content=item['content'],
                is_fake=item.get('is_fake', 0),
                media_bias=item['media_bias']
            )
            db.session.add(news)
        db.session.commit()
        return jsonify({'message': 'News added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
