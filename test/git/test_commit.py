# test_commit.py
# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php

from test.testlib import *
from git import *

class TestCommit(object):
	def setup(self):
		self.repo = Repo(GIT_REPO)

	@patch_object(Git, '_call_process')
	def test_bake(self, git):
		git.return_value = fixture('rev_list_single')

		commit = Commit(self.repo, **{'id': '4c8124ffcf4039d292442eeccabdeca5af5c5017'})
		commit.author # bake

		assert_equal("Tom Preston-Werner", commit.author.name)
		assert_equal("tom@mojombo.com", commit.author.email)

		assert_true(git.called)
		assert_equal(git.call_args, (('rev_list', '4c8124ffcf4039d292442eeccabdeca5af5c5017', '--', ''), {'pretty': 'raw', 'max_count': 1}))


	@patch_object(Git, '_call_process')
	def test_diff(self, git):
		git.return_value = fixture('diff_p')

		diffs = Commit.diff(self.repo, 'master')

		assert_equal(15, len(diffs))
		
		diff = diffs[0]
		assert_equal('.gitignore', diff.a_blob.path)
		assert_equal('.gitignore', diff.b_blob.path)
		assert_equal('4ebc8aea50e0a67e000ba29a30809d0a7b9b2666', diff.a_blob.id)
		assert_equal('2dd02534615434d88c51307beb0f0092f21fd103', diff.b_blob.id)
		
		assert_mode_644(diff.b_blob.mode)
		
		assert_equal(False, diff.new_file)
		assert_equal(False, diff.deleted_file)
		assert_equal("--- a/.gitignore\n+++ b/.gitignore\n@@ -1 +1,2 @@\n coverage\n+pkg", diff.diff)

		diff = diffs[5]
		assert_equal('lib/grit/actor.rb', diff.b_blob.path)
		assert_equal(None, diff.a_blob)
		assert_equal('f733bce6b57c0e5e353206e692b0e3105c2527f4', diff.b_blob.id)
		assert_equal( None, diff.a_mode )
		assert_equal(True, diff.new_file)

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M', 'master'), {'full_index': True}))

	@patch_object(Git, '_call_process')
	def test_diff_with_rename(self, git):
		git.return_value = fixture('diff_rename')

		diffs = Commit.diff(self.repo, 'rename')

		assert_equal(1, len(diffs))

		diff = diffs[0]
		assert_true(diff.renamed)
		assert_equal(diff.rename_from, 'AUTHORS')
		assert_equal(diff.rename_to, 'CONTRIBUTORS')

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M', 'rename'), {'full_index': True}))

	@patch_object(Git, '_call_process')
	def test_diff_with_two_commits(self, git):
		git.return_value = fixture('diff_2')

		diffs = Commit.diff(self.repo, '59ddc32', '13d27d5')

		assert_equal(3, len(diffs))

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M', '59ddc32', '13d27d5'), {'full_index': True}))

	@patch_object(Git, '_call_process')
	def test_diff_with_files(self, git):
		git.return_value = fixture('diff_f')

		diffs = Commit.diff(self.repo, '59ddc32', ['lib'])

		assert_equal(1, len(diffs))
		assert_equal('lib/grit/diff.rb', diffs[0].a_blob.path)

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M', '59ddc32', '--', 'lib'), {'full_index': True}))

	@patch_object(Git, '_call_process')
	def test_diff_with_two_commits_and_files(self, git):
		git.return_value = fixture('diff_2f')

		diffs = Commit.diff(self.repo, '59ddc32', '13d27d5', ['lib'])

		assert_equal(1, len(diffs))
		assert_equal('lib/grit/commit.rb', diffs[0].a_blob.path)

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M', '59ddc32', '13d27d5', '--', 'lib'), {'full_index': True}))

	@patch_object(Git, '_call_process')
	def test_diffs(self, git):
		git.return_value = fixture('diff_p')

		commit = Commit(self.repo, id='91169e1f5fa4de2eaea3f176461f5dc784796769', parents=['038af8c329ef7c1bae4568b98bd5c58510465493'])
		diffs = commit.diffs

		assert_equal(15, len(diffs))

		diff = diffs[0]
		assert_equal('.gitignore', diff.a_blob.path)
		assert_equal('.gitignore', diff.b_blob.path)
		assert_equal('4ebc8aea50e0a67e000ba29a30809d0a7b9b2666', diff.a_blob.id)
		assert_equal('2dd02534615434d88c51307beb0f0092f21fd103', diff.b_blob.id)
		assert_mode_644(diff.b_blob.mode)
		assert_equal(False, diff.new_file)
		assert_equal(False, diff.deleted_file)
		assert_equal("--- a/.gitignore\n+++ b/.gitignore\n@@ -1 +1,2 @@\n coverage\n+pkg", diff.diff)

		diff = diffs[5]
		assert_equal('lib/grit/actor.rb', diff.b_blob.path)
		assert_equal(None, diff.a_blob)
		assert_equal('f733bce6b57c0e5e353206e692b0e3105c2527f4', diff.b_blob.id)
		assert_equal(True, diff.new_file)

		assert_true(git.called)
		assert_equal(git.call_args, (('diff', '-M',
											  '038af8c329ef7c1bae4568b98bd5c58510465493',
											  '91169e1f5fa4de2eaea3f176461f5dc784796769',
									  ), {'full_index': True}))

	def test_diffs_on_initial_import(self):
		commit = Commit(self.repo, '33ebe7acec14b25c5f84f35a664803fcab2f7781')
		
		for diff in commit.diffs:
			assert isinstance(diff, Diff)
			assert isinstance(diff.a_blob, Blob) or isinstance(diff.b_blob, Blob)
			
			if diff.a_mode is not None:
				assert isinstance(diff.a_mode, int)
			if diff.b_mode is not None:
				isinstance(diff.b_mode, int)
			
			assert diff.diff is not None 	# can be empty
			
			if diff.renamed:
				assert diff.rename_from and diff.rename_to and diff.rename_from != diff.rename_to
			if diff.a_blob is None:
				assert diff.new_file and isinstance(diff.new_file, bool)
			if diff.b_blob is None:
				assert diff.deleted_file and isinstance(diff.deleted_file, bool)
		# END for each diff in initial import commit

	@patch_object(Git, '_call_process')
	def test_diffs_on_initial_import_with_empty_commit(self, git):
		git.return_value = fixture('show_empty_commit')

		commit = Commit(self.repo, id='634396b2f541a9f2d58b00be1a07f0c358b999b3')
		diffs = commit.diffs

		assert_equal([], diffs)

		assert_true(git.called)
		assert_equal(git.call_args, (('show', '634396b2f541a9f2d58b00be1a07f0c358b999b3', '-M'), {'full_index': True, 'pretty': 'raw'}))

	def test_diffs_with_mode_only_change(self):
		commit = Commit(self.repo, id='ccde80b7a3037a004a7807a6b79916ce2a1e9729')
		diffs = commit.diffs

		# in case of mode-only changes, there is no blob
		assert_equal(1, len(diffs))
		assert_equal(None, diffs[0].a_blob)
		assert_equal(None, diffs[0].b_blob)
		assert_mode_644(diffs[0].a_mode)
		assert_mode_755(diffs[0].b_mode)

	def test_stats(self):
		commit = Commit(self.repo, id='33ebe7acec14b25c5f84f35a664803fcab2f7781')
		stats = commit.stats
		
		def check_entries(d):
			assert isinstance(d, dict)
			for key in ("insertions", "deletions", "lines"):
				assert key in d
		# END assertion helper 
		assert stats.files 
		assert stats.total
		
		check_entries(stats.total) 
		assert "files" in stats.total
		
		for filepath, d in stats.files.items():
			check_entries(d)
		# END for each stated file
		
	@patch_object(Git, '_call_process')
	def test_rev_list_bisect_all(self, git):
		"""
		'git rev-list --bisect-all' returns additional information
		in the commit header.  This test ensures that we properly parse it.
		"""

		git.return_value = fixture('rev_list_bisect_all')

		revs = self.repo.git.rev_list('HEAD',
									  pretty='raw',
									  first_parent=True,
									  bisect_all=True)
		assert_true(git.called)

		commits = Commit.list_from_string(self.repo, revs)
		expected_ids = (
			'cf37099ea8d1d8c7fbf9b6d12d7ec0249d3acb8b',
			'33ebe7acec14b25c5f84f35a664803fcab2f7781',
			'a6604a00a652e754cb8b6b0b9f194f839fc38d7c',
			'8df638c22c75ddc9a43ecdde90c0c9939f5009e7',
			'c231551328faa864848bde6ff8127f59c9566e90',
		)
		for sha1, commit in zip(expected_ids, commits):
			assert_equal(sha1, commit.id)

	def test_str(self):
		commit = Commit(self.repo, id='abc')
		assert_equal ("abc", str(commit))

	def test_repr(self):
		commit = Commit(self.repo, id='abc')
		assert_equal('<git.Commit "abc">', repr(commit))

	def test_equality(self):
		commit1 = Commit(self.repo, id='abc')
		commit2 = Commit(self.repo, id='abc')
		commit3 = Commit(self.repo, id='zyx')
		assert_equal(commit1, commit2)
		assert_not_equal(commit2, commit3)
