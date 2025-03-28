from django.db import models
from django.contrib.auth.models import AbstractUser

class Registration(AbstractUser):
    phone = models.CharField(max_length=11, unique=True)
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone', 'dob']

    def __str__(self):
        return self.email
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(Registration, related_name='custom_groups')  # Change related_name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupExpense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    paid_by = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='paid_expenses')
    split_among = models.ManyToManyField(Registration, related_name='shared_expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Expense(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)  # Link expense to user
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('food', 'Food'),
            ('transportation', 'Transportation'),
            ('utilities', 'Utilities'),
            ('clothing','Clothing'),
            ('entertainment', 'Entertainment'),
            ('health', 'Health'),
            ('housing','Housing'),
            ('loans','Loans'),
            ('beauty','Beauty'),
            ('gifts','Gifts'),
            ('education','Education'),
            ('other', 'Other'),
        ]
    )

class Income(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('salary', 'Salary'),
            ('freelance', 'Freelance'),
            ('investment', 'Investment'),
            ('gift', 'Gift'),
            ('loan','Loan'),
            ('rental','Rental'),
            ('bonus','Bonus'),
            ('shares','Shares'),
            ('pension','Pension'),
            ('other', 'Other'),
        ]
    )