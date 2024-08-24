from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from typing import List
from marshmallow import ValidationError, fields
from connection import connection

app = Flask(__name__)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:lolol@localhost/LA_FITNESS'

class member_schema(ma.Schema):
    MemberID = fields.Int(dump_only=True)
    MemberName = fields.String(required=True)
    MemberEmail = fields.String()
    MemberPhone = fields.String()

    class Meta:
        fields = ("MemberID","MemberName","MemberEmail","MemberPhone", "MemberAddress")

MemberSchema = member_schema()
MembersSchema= member_schema(many = True)

class workoutsession_schema(ma.Schema):
    SessionID = fields.Int(dump_only=True)
    SessionDate = fields.Int(nullable = False)
    WorkoutType = fields.String(required=True)
    Duration = fields.Integer()
    
    class Meta:
        fields = ("SessionID","SessionDate","WorkoutType","Duration")


@app.route('/')
def home():
    return " Its hot here!"


@app.route('/Members', methods=['POST'])
def add_member():
    try:
        member_data = request.get_json()
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO Members (MemberName, MemberPhone, MemberEmail, MemberAddress) 
            VALUES (%s, %s, %s, %s)
            """
            
            new_member = (
            member_data['MemberName'], 
            member_data['MemberPhone'], 
            member_data['MemberEmail'], 
            member_data.get('MemberAddress',None)
            )
            
            cursor.execute(query,new_member)
            conn.commit()
            
            return jsonify({'Message': 'New member added!'}), 201
        except Exception as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'Error': 'Database connection failed'}), 500

@app.route('/Members/<int:id>', methods=['GET'])
def get_member(id):
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "Select * From Members WHERE MemberID = %s"
            cursor.execute(query,(id,))
            members = cursor.fetchone()
            if members:
                return jsonify(members), 200
            else:
                return ("There is no Member with that ID."), 404
            
        except Exception as e:
            print(f"Error: {e}"), 500
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        
          
            
@app.route('/Members/<int:id>', methods=['PUT'])
def update_member(id):
    conn = connection()
    try:
        member_data =  request.get_json()
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM Members WHERE MemberID = %s;"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify ({"Error": "Customer not found"}), 404
            query = """
            UPDATE Members 
            SET MemberName = %s, MemberPhone = %s, MemberEmail = %s 
            WHERE MemberID = %s
            """
            cursor.execute(query, (
                member_data['MemberName'],
                member_data['MemberPhone'],
                member_data['MemberEmail'],
                id
                ))
            conn.commit()
            return jsonify({'Message': f"Successfully updated customer {id}"}), 200
        
        except Exception as e:
            return jsonify({"Error": str(e)}), 500
        
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database connection failed."}), 500
    
@app.route('/Members/<int:id>', methods=['DELETE'])
def delete_member(id):
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Members WHERE MemberID = %s;"
            cursor.execute(query,(id,))
            conn.commit()
            return jsonify({"Message": f"Customer {id} was successfully deleted."})
        except Exception as e:
            return jsonify({"Error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database connection failed"}), 500
            

@app.route('/session', methods=['POST'])
def schedule_workout():
        try:
        # Get JSON data from request
            workout_data = request.get_json()
        except ValidationError as e:
            return jsonify(e.messages), 400
        # Extract data
        workout_type = workout_data.get('WorkoutType')
        member_id = workout_data.get('MemberID')
        session_date = workout_data.get('SessionDate')
        duration = workout_data.get('Duration')
        
        # Database connection
        conn = connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                
                # SQL query with placeholders for parameters
                query1 = "INSERT INTO WorkoutSession (WorkoutType, MemberID, SessionDate, Duration) VALUES (%s, %s, %s, %s)"
                
                # Execute query with parameters
                cursor.execute(query1, (workout_type, member_id, session_date, duration))
                conn.commit()
                
                return jsonify({"Message": 'New workout scheduled'}), 201
            
            except Exception as e:
                # Handle any unexpected errors
                return jsonify({"Error": str(e)}), 500
            
            finally:
                # Ensure the cursor and connection are always closed
                cursor.close()
                conn.close()
        else:
            return jsonify({"Error": "Database connection failed"}), 500  

@app.route('/session/<int:id>', methods=['PUT'])
def update_workout(id):
    try:
        workout_data = request.get_json()
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM WorkoutSession WHERE SessionID = %s;"
            cursor.execute(check_query,(id,))
            workout = cursor.fetchone()
            if not workout:
                return jsonify({"Error": "Workout not found."}), 404
            
            update_query ="""UPDATE WorkoutSession 
            SET WorkoutType = %s, SessionDate = %s, Duration = %s 
            WHERE SessionID = %s;
            """
            
            cursor.execute(update_query, 
            (workout_data['WorkoutType'], 
            workout_data['SessionDate'], 
            workout_data['Duration'],
            id
            ))
            
            conn.commit()
            return jsonify({"Message": f"Successfully updated Workout"}), 200
        except ValidationError as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"Error": "Database connection failed"}), 500

@app.route('/session/<int:id>', methods=['GET'])
def view_workout(id):
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM WorkoutSession WHERE MemberID = %s;"
            cursor.execute(check_query, (id,))
            workout_session = cursor.fetchone()
            
            if workout_session is None:
                return jsonify({'error': 'Workout session not found'}), 404
            
        
            return jsonify(workout_session)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
   app.run(debug= True)

