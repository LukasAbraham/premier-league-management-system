from django import forms
from .models import Regulation

class RegulationForm(forms.ModelForm):
    class Meta:
        model = Regulation
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    # Add Bootstrap classes to form labels
    def label_tag(self, label=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = 'form-label'
        return super().label_tag(label, attrs, label_suffix)
    
    def clean(self):
        cleaned_data = super().clean()
        win_points = cleaned_data.get('win_points')
        loss_points = cleaned_data.get('loss_points')
        draw_points = cleaned_data.get('draw_points')
        if win_points < draw_points or win_points < loss_points:
            self.add_error('win_points', "Points for a win must be greater than points for a loss and points for a draw")
        if draw_points < loss_points or draw_points > win_points:
            self.add_error('draw_points', "Points for a draw must be greater than points for a loss and lower than points for a win")
        if loss_points > draw_points or loss_points > win_points:
            self.add_error('loss_points', "Points for a loss must be lower that points for a draw and points for a win") 
        