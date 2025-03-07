import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models.chatbot import Chatbot
from models.assessment import MentalHealthAssessor
from models.user import User
from models.video_analyzer import VideoAnalyzer
from database.supabase_client import supabase, store_conversation, store_assessment, get_user_mood_scores
from utils.helpers import update_conversation_history, calculate_mood_score
import logging
from google.cloud import videointelligence
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

chatbot = Chatbot()
assessor = MentalHealthAssessor()
video_analyzer = VideoAnalyzer()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@login_manager.user_loader
def load_user(user_id):
    user_data = supabase.table('users').select('*').eq('id', user_id).execute()
    if user_data.data:
        return User(user_data.data[0])
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = supabase.table('users').insert({'email': email, 'password': hashed_password}).execute()
        if new_user.data:
            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Error creating account')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = supabase.table('users').select('*').eq('email', email).execute()
        if user_data.data and check_password_hash(user_data.data[0]['password'], password):
            user = User(user_data.data[0])
            login_user(user)
            return redirect(url_for('profile'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    mood_scores = get_user_mood_scores(current_user.id)
    average_score = sum(mood_scores) / len(mood_scores) if mood_scores else 0
    
    # Generate mood analyzer graph
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(mood_scores)), mood_scores, marker='o', linestyle='-', linewidth=2, markersize=8)
    plt.title('Mood Analysis Over Time', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Mood Score', fontsize=12)
    plt.ylim(0, 10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().set_facecolor('#f8f8f8')
    
    # Save the plot to a base64 encoded string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return render_template('profile.html', user=current_user, mood_scores=mood_scores, average_score=average_score, plot_data=plot_data)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        bot_response = chatbot.get_response(user_input)
        mood_score = calculate_mood_score(user_input)
        try:
            store_conversation(current_user.id, user_input, bot_response, mood_score)
            logging.info("Conversation stored successfully.")
        except Exception as e:
            logging.error(f"Error storing conversation: {str(e)}")
        return jsonify({'response': bot_response, 'mood_score': mood_score})
    
    # Retrieve past conversations
    conversations = supabase.table('conversations').select('*').eq('user_id', current_user.id).order('timestamp', desc=True).limit(20).execute()
    return render_template('chat.html', conversations=conversations.data)

@app.route('/assess', methods=['POST'])
@login_required
def assess():
    conversation_history = supabase.table('conversations').select('*').eq('user_id', current_user.id).order('timestamp', desc=True).limit(20).execute()
    if not conversation_history.data:
        return "Not enough conversation history for an assessment."
    
    history_text = "\n".join([f"User: {c['user_input']}\nBot: {c['bot_response']}" for c in reversed(conversation_history.data)])
    assessment = assessor.assess_mental_health(history_text)
    
    try:
        store_assessment(current_user.id, assessment)
        logging.info("Assessment stored successfully.")
    except Exception as e:
        logging.error(f"Error storing assessment: {str(e)}")
    
    return assessment

@app.route('/blog')
def blog():
    posts = supabase.table('blog_posts').select('*,users(email)').order('created_at', desc=True).execute()
    return render_template('blog.html', posts=posts.data)

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = supabase.table('blog_posts').insert({'user_id': current_user.id, 'title': title, 'content': content}).execute()
        if new_post.data:
            flash('Blog post created successfully.')
            return redirect(url_for('blog'))
        else:
            flash('Error creating blog post.')
    return render_template('new_post.html')

@app.route('/blog/<post_id>')
def view_post(post_id):
    post = supabase.table('blog_posts').select('*,users(email)').eq('id', post_id).single().execute()
    comments = supabase.table('comments').select('*,users(email)').eq('post_id', post_id).order('created_at', desc=True).execute()
    return render_template('view_post.html', post=post.data, comments=comments.data)

@app.route('/blog/<post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form['content']
    new_comment = supabase.table('comments').insert({'user_id': current_user.id, 'post_id': post_id, 'content': content}).execute()
    if new_comment.data:
        flash('Comment added successfully.')
    else:
        flash('Error adding comment.')
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/erase_chats', methods=['POST'])
@login_required
def erase_chats():
    try:
        # Delete all conversations for the current user
        supabase.table('conversations').delete().eq('user_id', current_user.id).execute()
        return jsonify({'success': True}), 200
    except Exception as e:
        logging.error(f"Error erasing chat history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/feed_analyzer', methods=['GET', 'POST'])
@login_required
def feed_analyzer():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No video file uploaded')
            return redirect(request.url)
        
        video = request.files['video']
        
        if video.filename == '':
            flash('No video selected')
            return redirect(request.url)
        
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(video_path)
            
            try:
                # Analyze video using Google Cloud Video Intelligence API
                client = videointelligence.VideoIntelligenceServiceClient()
                with io.open(video_path, 'rb') as file:
                    input_content = file.read()
                
                features = [videointelligence.Feature.LABEL_DETECTION]
                operation = client.annotate_video(
                    request={"features": features, "input_content": input_content}
                )
                result = operation.result(timeout=90)
                
                # Process video labels
                labels = result.annotation_results[0].segment_label_annotations
                label_descriptions = [label.entity.description for label in labels]
                
                # Analyze labels using the VideoAnalyzer
                score, analysis = video_analyzer.analyze_content(label_descriptions)
                safety_check = video_analyzer.get_content_safety(label_descriptions)
                
                # Clean up the uploaded file
                os.remove(video_path)
                
                return render_template('feed_analyzer_result.html', score=score, analysis=analysis, safety_check=safety_check)
            
            except Exception as e:
                logging.error(f"Error analyzing video: {str(e)}")
                flash('Error analyzing video. Please try again.')
                return redirect(request.url)
    
    return render_template('feed_analyzer.html')

if __name__ == '__main__':
    app.run(debug=True)

