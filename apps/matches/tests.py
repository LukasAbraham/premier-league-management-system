import os

from datetime import date, timedelta
import shutil
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from django.forms import formset_factory

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from apps.auth.models import UserProfile
from apps.matches.forms import GoalEventForm, MatchForm, ResultForm, BaseGoalEventFormSet

from apps.players.models import Player

from .models import GoalEvent, Match, Result
from apps.clubs.models import Club

class MatchModelTest(TestCase):
    def create_test_club(self, name):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
        )

    def create_test_player(self, name, club):
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1')
        self.club2 = self.create_test_club('Test Club 2')

    def test_create_match(self):
        match = Match.objects.create(
            round=1,
            time=timezone.now(),
            club1 = self.club1,
            club2 = self.club2,
        )
        match.save()

        self.assertEqual(match.__str__(), f"Round: 1 {self.club1.name} vs {self.club2.name}")

    def test_save_method_status_upcoming(self):
        match = Match(
            round=1,
            time=timezone.now() + timedelta(days=5),
            club1=self.club1,
            club2=self.club2,
        )
        match.save()
        
        self.assertEqual(match.status, 'U')

    def test_save_method_status_previous(self):
        match = Match(
            round=1,
            time=timezone.now() - timedelta(days=5),
            club1=self.club1,
            club2=self.club2,
        )
        match.save()

        self.assertEqual(match.status, 'P')

    def test_delete_method(self):
        match = Match.objects.create(
            round=1,
            time=timezone.now(),
            club1 = self.club1,
            club2 = self.club2,
        )

        match.save()
        self.assertEqual(Match.objects.count(), 1)

        match.delete()
        self.assertEqual(Match.objects.count(), 0)

class ResultModelTest(TestCase):
    def create_test_club(self, name):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
        )

    def create_test_player(self, name, club):
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
        )

    def create_test_match(self, round, club1, club2):
        return Match.objects.create(
            round=round,
            time=timezone.now() - timedelta(days=5),
            club1=club1,
            club2=club2,
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1')
        self.club2 = self.create_test_club('Test Club 2')
        self.match = self.create_test_match(1, self.club1, self.club2)

    def test_create_result(self):
        self.match.result = Result.objects.create(
            club1_goals=0,
            club2_goals=0,
            match=self.match,
        )
        self.match.save()

        self.assertIsInstance(self.match.result, Result)
        self.assertEqual(self.match.result.__str__(),
                         f"Result: {self.match.club1.name} 0 - 0 {self.match.club2.name}")

    def test_save_method_club1_wins(self):
        self.match.result = Result.objects.create(
            club1_goals=2,
            club2_goals=1,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.wins, 1)
        self.assertEqual(self.club2.club_stats.losses, 1)

    def test_save_method_club1_loses(self):
        self.match.result = Result.objects.create(
            club1_goals=1,
            club2_goals=2,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.losses, 1)
        self.assertEqual(self.club2.club_stats.wins, 1)

    def test_save_method_draws(self):
        self.match.result = Result.objects.create(
            club1_goals=1,
            club2_goals=1,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.draws, 1)
        self.assertEqual(self.club2.club_stats.draws, 1)

    def test_update_method(self):
        self.match.result = Result.objects.create(
            club1_goals=2,
            club2_goals=1,
            match=self.match,
        )
        self.match.save()

        self.assertEqual(self.club1.club_stats.wins, 1)
        self.assertEqual(self.club2.club_stats.losses, 1)

        old_result = self.match.result
        self.match.result.club2_goals = 3
        self.match.save()
        self.match.result.update(old_result=old_result)

        self.assertEqual(self.club1.club_stats.wins, 0)
        self.assertEqual(self.club1.club_stats.losses, 1)
        self.assertEqual(self.club2.club_stats.wins, 1)
        self.assertEqual(self.club2.club_stats.losses, 0)

    def test_delete_method_club1_wins(self):
        self.match.result = Result.objects.create(
            club1_goals=2,
            club2_goals=1,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.wins, 1)
        self.assertEqual(self.club2.club_stats.losses, 1)

        self.match.delete()

        self.assertEqual(self.club1.club_stats.wins, 0)
        self.assertEqual(self.club2.club_stats.losses, 0)

    def test_delete_method_club1_loses(self):
        self.match.result = Result.objects.create(
            club1_goals=1,
            club2_goals=2,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.losses, 1)
        self.assertEqual(self.club2.club_stats.wins, 1)

        self.match.delete()

        self.assertEqual(self.club1.club_stats.losses, 0)
        self.assertEqual(self.club2.club_stats.wins, 0)

    def test_delete_method_draws(self):
        self.match.result = Result.objects.create(
            club1_goals=1,
            club2_goals=1,
            match=self.match,
        )
        self.match.save()
        
        self.assertEqual(self.club1.club_stats.draws, 1)
        self.assertEqual(self.club2.club_stats.draws, 1)

        self.match.delete()

        self.assertEqual(self.club1.club_stats.draws, 0)
        self.assertEqual(self.club2.club_stats.draws, 0)

class GoalEventModelTest(TestCase):
    def create_test_club(self, name):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
        )

    def create_test_player(self, name, club):
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
        )

    def create_test_match(self, round, club1, club2):
        return Match.objects.create(
            round=round,
            time=timezone.now() - timedelta(days=5),
            club1=club1,
            club2=club2,
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1')
        self.club2 = self.create_test_club('Test Club 2')
        self.match = self.create_test_match(1, self.club1, self.club2)

    def test_create_goal_event(self):
        player = self.create_test_player('Test Player', self.club1)
        self.match.result = Result.objects.create(
            club1_goals=1,
            club2_goals=0,
            match=self.match,
        )
        self.match.save()
        goal_event = GoalEvent.objects.create(
            match=self.match,
            scoring_player=player,
            club=self.club1,
            type='N',
            time=75,
        )

        self.assertIsInstance(goal_event.match, Match)
        self.assertEqual(goal_event.__str__(),
                         f"Test Player scored a Normal at {goal_event.time}",)

    def test_save_method(self):
        player1 = self.create_test_player('Player 1', self.club1) 
        player2 = self.create_test_player('Player 2', self.club1)

        GoalEvent.objects.create(
            match=self.match,
            scoring_player=player1,
            assisting_player=player2,
            club=self.club1,
            type='N',
            time=75,
        )
        
        self.assertEqual(player1.player_stats.goals, 1)
        self.assertEqual(player2.player_stats.assists, 1)

    def test_update_method(self):
        player1 = self.create_test_player('Player 1', self.club1) 
        player2 = self.create_test_player('Player 2', self.club1)

        goal_event = GoalEvent.objects.create(
            match=self.match,
            scoring_player=player1,
            assisting_player=player2,
            club=self.club1,
            type='N',
            time=75,
        )
        
        self.assertEqual(player1.player_stats.goals, 1)
        self.assertEqual(player2.player_stats.assists, 1)

        old_goal_event = GoalEvent.objects.get(pk=goal_event.pk)
        goal_event.scoring_player = player2
        goal_event.assisting_player = player1
        goal_event.update(old_goal_event)

        self.assertEqual(player1.player_stats.assists, 1)
        self.assertEqual(player2.player_stats.goals, 1)

    def test_delete_method(self):
        player1 = self.create_test_player('Player 1', self.club1) 
        player2 = self.create_test_player('Player 2', self.club1)

        goal_event = GoalEvent.objects.create(
            match=self.match,
            scoring_player=player1,
            assisting_player=player2,
            club=self.club1,
            type='N',
            time=75,
        )

        self.assertEqual(player1.player_stats.goals, 1)
        self.assertEqual(player2.player_stats.assists, 1)

        goal_event.delete()

        player1.refresh_from_db()
        player2.refresh_from_db()

        self.assertEqual(player1.player_stats.goals, 0)
        self.assertEqual(player2.player_stats.assists, 0)

class MatchFormTest(TestCase):
    def create_test_club(self, name, status='V'):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
            status=status,
        )

    def create_test_match(self, round, club1, club2):
        return Match.objects.create(
            round=round,
            time=timezone.now() - timedelta(days=5),
            club1=club1,
            club2=club2,
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1', 'V')    
        self.club2 = self.create_test_club('Test Club 2', 'V')

    def test_valid_match(self):
        form_data = {
            'round': 1,
            'time': timezone.now(),
            'club1': self.club1.id,
            'club2': self.club2.id,
        }
        form = MatchForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_invalid_status(self):
        invalid_club = self.create_test_club('Invalid Club', 'I')
        form_data = {
            'round': 1,
            'time': timezone.now(),
            'club1': invalid_club.id,
            'club2': self.club2.id
        }

        form = MatchForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_club_against_self(self):
        form_data = {
            'round': 1,
            'time': timezone.now(),
            'club1': self.club1.id,
            'club2': self.club1.id
        }
        form = MatchForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_club_compete_twice(self):
        club = self.create_test_club('Evil Club', 'V')
        self.create_test_match(1, club, self.club1)
        form_data = {
            'round': 2,
            'time': timezone.now(),
            'club1': club.id,
            'club2': self.club1.id
        }
        form = MatchForm(data=form_data)
        self.assertTrue(form.is_valid())

class ResultFormTest(TestCase):
    def create_test_club(self, name, status='V'):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
            status=status,
        )

    def create_test_match(self, round, time, club1, club2):
        return Match.objects.create(
            round=round,
            time=time,
            club1=club1,
            club2=club2,
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1', 'V')    
        self.club2 = self.create_test_club('Test Club 2', 'V')

    def test_add_result_upcoming_match(self):
        match = self.create_test_match(1, timezone.now() + timedelta(days=5), self.club1, self.club2)
        match.save()

        form_data = {
            'club1_goals': 2,
            'club2_goals': 1,
        }
        form = ResultForm(data=form_data, match=match)
        self.assertFalse(form.is_valid())

    def test_add_result_completed_match(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.save()

        form_data = {
            'club1_goals': 2,
            'club2_goals': 1,
        }
        form = ResultForm(data=form_data, match=match)
        self.assertTrue(form.is_valid())

class GoalEventFormTest(TestCase):
    def create_test_club(self, name, status='V'):
        return Club.objects.create(
            name=name,
            stadium='Anfield',
            status=status,
        )

    def create_test_player(self, name, club):
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
        )

    def create_test_match(self, round, time, club1, club2):
        return Match.objects.create(
            round=round,
            time=time,
            club1=club1,
            club2=club2,
        )

    def setUp(self):
        self.club1 = self.create_test_club('Test Club 1')
        self.club2 = self.create_test_club('Test Club 2')

    def test_valid_goal_event(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        player1 = self.create_test_player('Player 1', self.club1)
        player2 = self.create_test_player('Player 2', self.club1)

        form_data = {
            'scoring_player': player1.id,
            'assisting_player': player2.id,
            'type': 'N',
            'time': 75,
            'club': self.club1.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertTrue(form.is_valid())

    def test_player_assist_self(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        player = self.create_test_player('Player 1', self.club1)

        form_data = {
            'scoring_player': player.id,
            'assisting_player': player.id,
            'type': 'N',
            'time': 75,
            'club': self.club1.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

    def test_player_score_but_assist_by_player_from_other_club(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        club1_player = self.create_test_player('Player From Club 1', self.club1)
        club2_player = self.create_test_player('Player From Club 2', self.club2)

        form_data = {
            'scoring_player': club1_player.id,
            'assisting_player': club2_player.id,
            'type': 'N',
            'time': 75,
            'club': self.club1.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

    def test_invalid_goal_type(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 0,
            club2_goals = 1,
            match=match,
        )
        player1 = self.create_test_player('Player 1', self.club1)
        player2 = self.create_test_player('Player 2', self.club1)

        form_data = {
            'scoring_player': player1.id,
            'assisting_player': player2.id,
            'type': 'N',
            'time': 75,
            'club': self.club2.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

    def test_invalid_goal_time(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        player1 = self.create_test_player('Player 1', self.club1)
        player2 = self.create_test_player('Player 2', self.club1)

        form_data = {
            'scoring_player': player1.id,
            'assisting_player': player2.id,
            'type': 'N',
            'time': 150,
            'club': self.club1.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

    def test_club_not_in_match(self):
        match = self.create_test_match(1, timezone.now() - timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        player1 = self.create_test_player('Player 1', self.club1)
        player2 = self.create_test_player('Player 2', self.club1)

        some_club = self.create_test_club('Some Club', 'V')

        form_data = {
            'scoring_player': player1.id,
            'assisting_player': player2.id,
            'type': 'N',
            'time': 75,
            'club': some_club.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

    def test_adding_goal_event_for_upcoming_match(self):
        match = self.create_test_match(1, timezone.now() + timedelta(days=5), self.club1, self.club2)
        match.result = Result.objects.create(
            club1_goals = 1,
            club2_goals = 0,
            match=match,
        )
        player1 = self.create_test_player('Player 1', self.club1)
        player2 = self.create_test_player('Player 2', self.club1)

        form_data = {
            'scoring_player': player1.id,
            'assisting_player': player2.id,
            'type': 'N',
            'time': 75,
            'club': self.club1.id,
        }
        form = GoalEventForm(data=form_data, match=match)

        self.assertFalse(form.is_valid())

class MatchViewTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_club(self, name, status='V'):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            return Club.objects.create(
                name=name,
                stadium='Anfield',
                status=status,
                logo=logo,
            )

    def create_test_player(self, name, club):
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
        )

    def create_test_match(self, round, time, club1, club2):
        return Match.objects.create(
            round=round,
            time=time,
            club1=club1,
            club2=club2,
        )

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.client = Client() 

        self.admin = User.objects.create(username='admin', password='admin123')
        UserProfile.objects.create(user=self.admin, type='admin')

        self.client.login(username='admin', password='admin123')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_index_view(self):
        clubs = [self.create_test_club(f"Club {i + 1}") for i in range(4)]
        match1 = self.create_test_match(
            1,
            timezone.now() + timedelta(days=5),
            clubs[0],
            clubs[1],
        )
        match2 = self.create_test_match(
            1,
            timezone.now() - timedelta(days=5),
            clubs[2],
            clubs[3],
        )

        url = reverse('matches:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matches/index.html')

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 4)

        self.assertIn('matches_list', response.context)
        self.assertEqual(len(response.context['matches_list']), 2)
        self.assertEqual(response.context['matches_list'][0].id, match1.id)
        self.assertEqual(response.context['matches_list'][1].id, match2.id)

    def test_add_match(self):
        url = reverse('matches:add') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matches/add.html')
        self.assertIsInstance(response.context['form'], MatchForm)

        clubs = [self.create_test_club(f"Club {i + 1}") for i in range(2)]  # Create test clubs
        data = {
            'round': 1,
            'time': timezone.now() + timedelta(days=3),
            'club1': clubs[0].id,
            'club2': clubs[1].id,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Match.objects.count(), 1)

    def test_add_result_view_get(self):
        match = self.create_test_match(
            1,
            timezone.now(),
            self.create_test_club('Club 1'),
            self.create_test_club('Club 2')
        )

        url = reverse('matches:add_result', args=[match.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matches/add_result.html')
        self.assertIsInstance(response.context['form'], ResultForm)
        self.assertIn('match', response.context)
        self.assertEqual(response.context['match'], match)

    def test_add_result_view_post(self):
        match = self.create_test_match(
            1,
            timezone.now() - timedelta(days=5),
            self.create_test_club('Club 1'),
            self.create_test_club('Club 2')
        )

        url = reverse('matches:add_result', args=[match.id])
        data = {
            'club1_goals': 2,
            'club2_goals': 1,
            'match': match
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('matches:add_goal_events', args=[match.id]))
        self.assertEqual(Result.objects.filter(match=match).count(), 1)

    def test_edit_view(self):
        match = self.create_test_match(
            1,
            timezone.now() - timedelta(days=3),
            self.create_test_club('Club 1'),
            self.create_test_club('Club 2')
        )

        url = reverse('matches:edit', args=[match.id])
        data = {
            'round': 1,
            'time': timezone.now() + timedelta(days=5),
            'club1': match.club1.id,
            'club2': match.club2.id,
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'matches/add.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], MatchForm)

    def test_delete_view(self):
        match = self.create_test_match(
            1,
            timezone.now(),
            self.create_test_club('Club 1'),
            self.create_test_club('Club 2')
        )

        url = reverse('matches:delete', args=[match.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Match.objects.filter(pk=match.id).exists())

    def test_detail_view(self):
        club1 = self.create_test_club('Club 1')
        club2 = self.create_test_club('Club 2')
        match = self.create_test_match(
            1,
            timezone.now() - timedelta(days=5),
            club1 = club1,
            club2 = club2,
        )
        result = Result.objects.create(match=match, club1_goals=2, club2_goals=1)

        player1 = self.create_test_player('Player 1', club1)
        player2 = self.create_test_player('Player 2', club2)

        goal_event_1 = GoalEvent.objects.create(
            match=match,
            scoring_player=player1,
            club=club1,
            type='N',
            time=10,
        )
        goal_event_2 = GoalEvent.objects.create(
            match=match,
            scoring_player=player2,
            club=club2,
            type='FK',
            time=32,
        )

        url = reverse('matches:view', args=[match.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matches/view.html')
        self.assertIn('match', response.context)
        self.assertEqual(response.context['match'].id, match.id)
        self.assertIn('result', response.context)
        self.assertEqual(response.context['result'], result)
        self.assertIn('goal_events', response.context)
        self.assertCountEqual(response.context['goal_events'], [goal_event_1, goal_event_2])
