import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

# Load the MySQL root password from environment variables
mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {'host': 'localhost',
          'database_name': 'hr',
          'user': 'root',
          'password': mysql_root_password}

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database_name']}"))

Base = declarative_base()

# Company model
class Company(Base):
    __tablename__ = 'Company'
    id = Column(Integer, primary_key=True)
    rut = Column(String(20))  # Equivalent to 'rut'
    name = Column(String(100))
    address = Column(String(255))
    phone = Column(String(20))
    industry = Column(String(100))  # Equivalent to 'giro'

# Employee model
class Employee(Base):
    __tablename__ = 'Employee'
    id = Column(Integer, primary_key=True)
    rut = Column(String(20))  # Equivalent to 'rut'
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date)
    start_date = Column(Date)
    phone = Column(String(20))
    salary = Column(DECIMAL(10, 2))
    nationality = Column(String(50))
    contracts = relationship('Contract', back_populates='employee')
    vacations = relationship('Vacation', back_populates='employee')
    evaluations = relationship('Evaluation', back_populates='employee')
    trainings = relationship('Training', back_populates='employee')
    remunerations = relationship('Remuneration', back_populates='employee')
    positions = relationship('JobPosition', secondary='EmployeePosition', back_populates='employees')

# Position model
class JobPosition(Base):
    __tablename__ = 'JobPosition'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    department_id = Column(Integer, ForeignKey('Department.id'))  # Foreign key to Department
    department = relationship('Department', back_populates='job_positions')  # Relationship to Department
    employees = relationship('Employee', secondary='EmployeePosition', back_populates='positions')  # Relationship to Employee

# EmployeePosition association table (Many-to-Many relationship between Employee and JobPosition)
class EmployeePosition(Base):
    __tablename__ = 'EmployeePosition'
    employee_id = Column(Integer, ForeignKey('Employee.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('JobPosition.id'), primary_key=True)

# Pension Fund model (AFP)
class AFP(Base):
    __tablename__ = 'AFP'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    commission_percentage = Column(DECIMAL(5, 2))
    remunerations = relationship('Remuneration', back_populates='pension_fund')

# Department model
class Department(Base):
    __tablename__ = 'Department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    contracts = relationship('Contract', back_populates='department')
    job_positions = relationship('JobPosition', back_populates='department')  # Relationship to JobPosition

# Vacation model
class Vacation(Base):
    __tablename__ = 'Vacation'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    days_taken = Column(Integer)
    accumulated_days = Column(Integer)
    long_service_employee = Column(Boolean)  # Equivalent to 'colaborador_antiguo'
    employee = relationship('Employee', back_populates='vacations')

# Evaluation model
class Evaluation(Base):
    __tablename__ = 'Evaluation'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    evaluation_date = Column(Date)
    evaluator = Column(String(100))
    evaluation_factor = Column(DECIMAL(5, 2))
    rating = Column(String(50))  # Good, average, bad/deficient
    comments = Column(Text)
    employee = relationship('Employee', back_populates='evaluations')

# Training model
class Training(Base):
    __tablename__ = 'Training'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    training_date = Column(Date)
    course = Column(String(100))
    score = Column(DECIMAL(5, 2))
    institution = Column(String(100))
    comments = Column(Text)
    employee = relationship('Employee', back_populates='trainings')

# Remuneration model
class Remuneration(Base):
    __tablename__ = 'Remuneration'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    afp_id = Column(Integer, ForeignKey('AFP.id'))
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    gross_amount = Column(DECIMAL(10, 2))
    tax = Column(DECIMAL(5, 2))
    deductions = Column(DECIMAL(10, 2))
    bonus = Column(DECIMAL(10, 2))
    welfare_contribution = Column(DECIMAL(10, 2))
    net_amount = Column(DECIMAL(10, 2))
    employee = relationship('Employee', back_populates='remunerations')
    pension_fund = relationship('AFP', back_populates='remunerations')
    health_plan = relationship('HealthPlan', back_populates='remunerations')
    bonuses = relationship("Bonus", back_populates="remuneration")

# HealthPlan model
class HealthPlan(Base):
    __tablename__ = 'HealthPlan'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    type = Column(String(50))
    public_health = relationship('Fonasa', back_populates='health_plan')
    private_health = relationship('Isapre', back_populates='health_plan')
    remunerations = relationship('Remuneration', back_populates='health_plan')

# Public Health model (Fonasa)
class Fonasa(Base):
    __tablename__ = 'Fonasa'
    id = Column(Integer, primary_key=True)
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    discount = Column(DECIMAL(10, 2))  # Equivalent to 'descuento'
    health_plan = relationship('HealthPlan', back_populates='fonasa')

# PrivateHealth model (Isapre)
class Isapre(Base):
    __tablename__ = 'Isapre'
    id = Column(Integer, primary_key=True)
    health_plan_id = Column(Integer, ForeignKey('HealthPlan.id'))
    discount = Column(DECIMAL(10, 2)) 
    health_plan = relationship('HealthPlan', back_populates='isapre')

# Bonus model
class Bonus(Base):
    __tablename__ = 'Bonus'
    id = Column(Integer, primary_key=True)
    remuneration_id = Column(Integer, ForeignKey('Remuneration.id')) 
    benefit = Column(DECIMAL(10, 2))  
    remuneration = relationship("Remuneration", back_populates="bonuses")

# Contract model
class Contract(Base):
    __tablename__ = 'Contract'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    contract_type = Column(String(50))  # Fixed, temporary, replacement, permanent (contrata, suplencia, reemplazo, planta)
    start_date = Column(Date)
    end_date = Column(Date)
    classification = Column(String(50))  # Auxiliary, administrative, technical, professional, executive (escalafon)
    department_id = Column(Integer, ForeignKey('Department.id'))
    registration_date = Column(Date)
    employee = relationship('Employee', back_populates='contracts')
    department = relationship('Department', back_populates='contracts')

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Method to set hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Method to check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Create the tables in the database
Base.metadata.create_all(engine)