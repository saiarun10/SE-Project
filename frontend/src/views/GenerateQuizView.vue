```vue
<template>
  <Navbar />
  <div class="container py-4 px-3 px-md-4">
    <Alert v-if="alert.visible" :message="alert.message" :type="alert.type" @close="alert.visible = false" />
    <h2 class="mb-4 text-center text-black fw-bold">Admin, Generate Quiz</h2>
    <div class="shadow-lg p-3 p-md-4 mx-auto rounded-4 border" style="max-width: 720px;">
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Choose Lesson</label>
        <select v-model="selectedLesson" class="form-select" @change="fetchModules" :disabled="isSubmitting">
          <option value="">-- Choose Lesson --</option>
          <option v-for="lesson in lessons" :key="lesson.lesson_id" :value="lesson.lesson_id">{{ lesson.lesson_name }}</option>
        </select>
      </div>
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Choose Module</label>
        <select v-model="selectedModule" class="form-select" @change="fetchTopics" :disabled="!selectedLesson || isSubmitting">
          <option value="">-- Choose Module --</option>
          <option v-for="module in modules" :key="module.module_id" :value="module.module_id">{{ module.module_title }}</option>
        </select>
      </div>
      <div class="form-group mb-3">
        <label class="form-label text-black fw-semibold">Choose Topic</label>
        <select v-model="selectedTopic" class="form-select" :disabled="!selectedModule || isSubmitting">
          <option value="">-- Choose Topic --</option>
          <option v-for="topic in topics" :key="topic.topic_id" :value="topic.topic_id">{{ topic.topic_title }}</option>
        </select>
      </div>
      <div class="text-center mb-4">
        <button class="btn btn-primary" @click="fetchQuizzes" :disabled="!selectedLesson || !selectedModule || !selectedTopic || isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
          Submit
        </button>
      </div>
      <div v-if="quizzes.length" class="table-responsive">
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Quiz Title</th>
              <th>Duration (min)</th>
              <th>Visibility</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="quiz in paginatedQuizzes" :key="quiz.quiz_id">
              <td>{{ quiz.quiz_title }}</td>
              <td>{{ quiz.duration_minutes }}</td>
              <td>{{ quiz.is_visible ? 'Visible' : 'Hidden' }}</td>
              <td>
                <button v-if="quiz.questions && quiz.questions.length" class="btn btn-info btn-sm me-2" @click="viewQuestions(quiz.quiz_id)" :disabled="isSubmitting">
                  <i class="fas fa-eye"></i> View Questions
                </button>
                <button v-else class="btn btn-primary btn-sm me-2" @click="createFirstQuestionModal(quiz.quiz_id)" :disabled="isSubmitting">
                  <i class="fas fa-plus"></i> Create First Question
                </button>
                <button class="btn btn-warning btn-sm me-2" @click="toggleQuizVisibility(quiz)" :disabled="isSubmitting">
                  <i class="fas fa-eye" v-if="quiz.is_visible"></i><i class="fas fa-eye-slash" v-else></i> {{ quiz.is_visible ? 'Hide' : 'Show' }}
                </button>
                <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.quiz_id)" :disabled="isSubmitting">
                  <i class="fas fa-trash"></i> Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <nav>
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ 'disabled': currentQuizPage === 1 }">
              <button class="page-link" @click="changeQuizPage(-1)">&lt;</button>
            </li>
            <li class="page-item" v-for="page in quizPageCount" :key="page" :class="{ 'active': currentQuizPage === page }">
              <button class="page-link" @click="currentQuizPage = page">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ 'disabled': currentQuizPage === quizPageCount }">
              <button class="page-link" @click="changeQuizPage(1)">&gt;</button>
            </li>
          </ul>
        </nav>
        <div class="text-center mt-3">
          <button class="btn btn-success" @click="generateQuizModal" :disabled="isSubmitting">Generate New Quiz</button>
        </div>
      </div>
      <div v-else-if="selectedTopic" class="text-center">
        <p>No quizzes available for this topic.</p>
        <button class="btn btn-success" @click="generateQuizModal" :disabled="isSubmitting">Generate Quiz</button>
      </div>
    </div>

    <!-- View/Edit Questions Modal -->
    <div v-if="viewQuestionsModalVisible" class="modal" tabindex="-1" style="display: block;">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Questions for {{ selectedQuizTitle }}</h5>
            <button type="button" class="btn-close" @click="closeViewQuestionsModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedQuizQuestions.length === 0" class="text-center">
              <p>No questions available.</p>
              <button class="btn btn-primary btn-sm" @click="createQuestionModal">Create First Question</button>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Question</th>
                    <th>Option 1</th>
                    <th>Option 2</th>
                    <th>Option 3</th>
                    <th>Option 4</th>
                    <th>Correct Answer</th>
                    <th>Score</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(question, index) in paginatedQuestions" :key="question.question_id">
                    <td>{{ (currentQuestionPage - 1) * itemsPerPage + index + 1 }}</td>
                    <td>{{ question.question_text }}</td>
                    <td>{{ question.option1 }}</td>
                    <td>{{ question.option2 }}</td>
                    <td>{{ question.option3 }}</td>
                    <td>{{ question.option4 }}</td>
                    <td>{{ question.correct_answer }}</td>
                    <td>{{ question.score_points }}</td>
                    <td>
                      <button class="btn btn-warning btn-sm me-2" @click="editQuestion(question)">
                        <i class="fas fa-pen"></i>
                      </button>
                      <button class="btn btn-danger btn-sm" @click="deleteQuestion(question.question_id)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <nav>
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ 'disabled': currentQuestionPage === 1 }">
                    <button class="page-link" @click="changeQuestionPage(-1)">&lt;</button>
                  </li>
                  <li class="page-item" v-for="page in questionPageCount" :key="page" :class="{ 'active': currentQuestionPage === page }">
                    <button class="page-link" @click="currentQuestionPage = page">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ 'disabled': currentQuestionPage === questionPageCount }">
                    <button class="page-link" @click="changeQuestionPage(1)">&gt;</button>
                  </li>
                </ul>
              </nav>
              <div class="text-center mt-3">
                <button class="btn btn-primary" @click="createQuestionModal">Add Another Question</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeViewQuestionsModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Quiz Modal -->
    <div v-if="generateQuizModalVisible" class="modal" tabindex="-1" style="display: block;">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Generate New Quiz</h5>
            <button type="button" class="btn-close" @click="closeGenerateQuizModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createQuiz" novalidate>
              <div class="form-group mb-3">
                <label class="form-label">Quiz Title</label>
                <input v-model="newQuiz.quiz_title" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuiz.quiz_title.$error }" />
                <div v-for="error in v$.newQuiz.quiz_title.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
              </div>
              <div class="form-group mb-3">
                <label class="form-label">Duration (minutes)</label>
                <input v-model.number="newQuiz.duration_minutes" type="number" class="form-control" required :class="{ 'is-invalid': v$.newQuiz.duration_minutes.$error }" />
                <div v-for="error in v$.newQuiz.duration_minutes.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting || v$.newQuiz.$invalid">
                  Create Quiz
                </button>
                <button type="button" class="btn btn-secondary ms-2" @click="closeGenerateQuizModal">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Question Modal -->
    <div v-if="createModalVisible" class="modal" tabindex="-1" style="display: block;">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingQuestion ? 'Edit Question' : 'Create Question' }}</h5>
            <button type="button" class="btn-close" @click="closeCreateModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuestion" novalidate>
              <div class="form-group mb-3">
                <label class="form-label">Question Text</label>
                <input v-model="newQuestion.question_text" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.question_text.$error }" />
                <div v-for="error in v$.newQuestion.question_text.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
              </div>
              <div class="row">
                <div class="col-md-6 form-group mb-3">
                  <label class="form-label">Option 1</label>
                  <input v-model="newQuestion.option1" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.option1.$error }" />
                  <div v-for="error in v$.newQuestion.option1.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
                </div>
                <div class="col-md-6 form-group mb-3">
                  <label class="form-label">Option 2</label>
                  <input v-model="newQuestion.option2" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.option2.$error }" />
                  <div v-for="error in v$.newQuestion.option2.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 form-group mb-3">
                  <label class="form-label">Option 3</label>
                  <input v-model="newQuestion.option3" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.option3.$error }" />
                  <div v-for="error in v$.newQuestion.option3.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
                </div>
                <div class="col-md-6 form-group mb-3">
                  <label class="form-label">Option 4</label>
                  <input v-model="newQuestion.option4" type="text" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.option4.$error }" />
                  <div v-for="error in v$.newQuestion.option4.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
                </div>
              </div>
              <div class="form-group mb-3">
                <label class="form-label">Correct Answer</label>
                <select v-model="newQuestion.correct_answer" class="form-select" required :class="{ 'is-invalid': v$.newQuestion.correct_answer.$error }">
                  <option v-for="(option, index) in [newQuestion.option1, newQuestion.option2, newQuestion.option3, newQuestion.option4]" :key="index" :value="option" :disabled="!option">
                    {{ option || `Option ${index + 1}` }}
                  </option>
                </select>
                <div v-for="error in v$.newQuestion.correct_answer.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
              </div>
              <div class="form-group mb-3">
                <label class="form-label">Score Points</label>
                <input v-model.number="newQuestion.score_points" type="number" class="form-control" required :class="{ 'is-invalid': v$.newQuestion.score_points.$error }" />
                <div v-for="error in v$.newQuestion.score_points.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting || v$.newQuestion.$invalid">
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingQuestion ? 'Update Question' : 'Add Question' }}
                </button>
                <button type="button" class="btn btn-secondary ms-2" @click="closeCreateModal">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
  <AppFooter />
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import useVuelidate from '@vuelidate/core';
import { required, minValue } from '@vuelidate/validators';

export default {
  name: 'GenerateQuiz',
  components: { Alert, Navbar, AppFooter },
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      lessons: [],
      modules:

 [],
      topics: [],
      quizzes: [],
      selectedLesson: '',
      selectedModule: '',
      selectedTopic: '',
      selectedQuiz: null,
      selectedQuizTitle: '',
      selectedQuizQuestions: [],
      viewQuestionsModalVisible: false,
      createModalVisible: false,
      generateQuizModalVisible: false,
      editingQuestion: false,
      newQuiz: {
        quiz_title: '',
        duration_minutes: 30
      },
      newQuestion: {
        question_id: null,
        quiz_id: null,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: '',
        score_points: 1
      },
      isSubmitting: false,
      alert: { visible: false, message: '', type: 'notification' },
      itemsPerPage: 5,
      currentQuizPage: 1,
      currentQuestionPage: 1
    };
  },
  validations() {
    return {
      newQuiz: {
        quiz_title: { required },
        duration_minutes: { required, minValue: minValue(1) }
      },
      newQuestion: {
        question_text: { required },
        option1: { required },
        option2: { required },
        option3: { required },
        option4: { required },
        correct_answer: { required },
        score_points: { required, minValue: minValue(1) }
      }
    };
  },
  computed: {
    paginatedQuizzes() {
      const start = (this.currentQuizPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.quizzes.slice(start, end);
    },
    quizPageCount() {
      return Math.ceil(this.quizzes.length / this.itemsPerPage);
    },
    paginatedQuestions() {
      const start = (this.currentQuestionPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.selectedQuizQuestions.slice(start, end);
    },
    questionPageCount() {
      return Math.ceil(this.selectedQuizQuestions.length / this.itemsPerPage);
    }
  },
  methods: {
    changeQuizPage(page) {
      if (typeof page === 'number') {
        this.currentQuizPage = page;
      } else {
        this.currentQuizPage = Math.max(1, Math.min(this.quizPageCount, this.currentQuizPage + page));
      }
    },
    changeQuestionPage(page) {
      if (typeof page === 'number') {
        this.currentQuestionPage = page;
      } else {
        this.currentQuestionPage = Math.max(1, Math.min(this.questionPageCount, this.currentQuestionPage + page));
      }
    },
    async fetchLessons() {
      try {
        this.isSubmitting = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_all_lessons`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.lessons = response.data;
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to load lessons', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async fetchModules() {
      if (!this.selectedLesson) {
        this.modules = [];
        this.selectedModule = '';
        this.topics = [];
        this.selectedTopic = '';
        this.quizzes = [];
        return;
      }
      try {
        this.isSubmitting = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
        this.selectedModule = '';
        this.topics = [];
        this.selectedTopic = '';
        this.quizzes = [];
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to load modules', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async fetchTopics() {
      if (!this.selectedLesson || !this.selectedModule) {
        this.topics = [];
        this.selectedTopic = '';
        this.quizzes = [];
        return;
      }
      try {
        this.isSubmitting = true;
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topics`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.topics = response.data;
        this.selectedTopic = '';
        this.quizzes = [];
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to load topics', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async fetchQuizzes() {
      if (!this.selectedLesson || !this.selectedModule || !this.selectedTopic) {
        this.quizzes = [];
        return;
      }
      try {
        this.isSubmitting = true;
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes`,
          {
            headers: { Authorization: `Bearer ${this.$store.state.token}` }
          }
        );
        console.log("quizzes data:", response.data);
        this.quizzes = response.data;
        for (const quiz of this.quizzes) {
          await this.fetchQuestionsForQuiz(quiz.quiz_id);
        }

        this.currentQuizPage = 1;
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to load quizzes', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async fetchQuestionsForQuiz(quizId) {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${quizId}/questions`,
          {
            headers: { Authorization: `Bearer ${this.$store.state.token}` }
          }
        );
        const quiz = this.quizzes.find(q => q.quiz_id === quizId);
        if (quiz) {
          quiz.questions = response.data;
        }
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || `Failed to load questions for quiz ${quizId}`, type: 'error' };
      }
    },
    async generateQuizModal() {
      this.generateQuizModalVisible = true;
      this.newQuiz = {
        quiz_title: this.topics.find(t => t.topic_id === this.selectedTopic)?.topic_title
          ? `Quiz for Topic ${this.topics.find(t => t.topic_id === this.selectedTopic).topic_title}`
          : 'New Quiz',
        duration_minutes: 30
      };
      this.v$.newQuiz.$reset();
    },
    async createQuiz() {
      const isValid = await this.v$.newQuiz.$validate();
      if (!isValid) {
        this.alert = { visible: true, message: 'Please fill all required fields correctly', type: 'error' };
        return;
      }
      try {
        this.isSubmitting = true;
        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quiz/create`,
          this.newQuiz,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        const newQuiz = response.data;
        newQuiz.questions = [];
        this.quizzes.push(newQuiz);
        this.alert = { visible: true, message: 'Quiz created successfully', type: 'success' };
        this.closeGenerateQuizModal();
        this.createFirstQuestionModal(newQuiz.quiz_id);
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to create quiz', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    createFirstQuestionModal(quizId) {
      this.selectedQuiz = quizId;
      const quiz = this.quizzes.find(q => q.quiz_id === quizId);
      this.selectedQuizTitle = quiz ? quiz.quiz_title : 'Unknown Quiz';
      this.createModalVisible = true;
      this.newQuestion = {
        question_id: null,
        quiz_id: quizId,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: '',
        score_points: 1
      };
      this.editingQuestion = false;
      this.v$.newQuestion.$reset();
    },
    createQuestionModal() {
      this.createModalVisible = true;
      this.newQuestion = {
        question_id: null,
        quiz_id: this.selectedQuiz,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: '',
        score_points: 1
      };
      this.editingQuestion = false;
      this.v$.newQuestion.$reset();
    },
    async saveQuestion() {
      const isValid = await this.v$.newQuestion.$validate();
      if (!isValid) {
        this.alert = { visible: true, message: 'Please fill all required fields correctly', type: 'error' };
        return;
      }
      try {
        this.isSubmitting = true;
        const payload = {
          question_text: this.newQuestion.question_text,
          option1: this.newQuestion.option1,
          option2: this.newQuestion.option2,
          option3: this.newQuestion.option3,
          option4: this.newQuestion.option4,
          correct_answer: this.newQuestion.correct_answer,
          score_points: this.newQuestion.score_points
        };
        const endpoint = this.editingQuestion
          ? `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${this.newQuestion.quiz_id}/question/${this.newQuestion.question_id}/update`
          : `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${this.newQuestion.quiz_id}/question/create`;
        const response = await axios({
          method: this.editingQuestion ? 'put' : 'post',
          url: endpoint,
          data: payload,
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.alert = { visible: true, message: this.editingQuestion ? 'Question updated successfully' : 'Question created successfully', type: 'success' };
        this.closeCreateModal();
        await this.fetchQuestionsForQuiz(this.selectedQuiz);
        if (this.viewQuestionsModalVisible) this.viewQuestions(this.selectedQuiz);
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || (this.editingQuestion ? 'Failed to update question' : 'Failed to create question'), type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    viewQuestions(quizId) {
      this.selectedQuiz = quizId;
      const quiz = this.quizzes.find(q => q.quiz_id === quizId);
      this.selectedQuizTitle = quiz ? quiz.quiz_title : 'Unknown Quiz';
      this.selectedQuizQuestions = quiz ? quiz.questions || [] : [];
      this.currentQuestionPage = 1;
      this.viewQuestionsModalVisible = true;
    },
    editQuestion(question) {
      this.newQuestion = { ...question, score_points: question.score_points || 1 };
      this.editingQuestion = true;
      this.createModalVisible = true;
      this.v$.newQuestion.$reset();
    },
    async deleteQuestion(questionId) {
      if (!confirm('Are you sure you want to delete this question?')) return;
      try {
        this.isSubmitting = true;
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${this.selectedQuiz}/question/${questionId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.selectedQuizQuestions = this.selectedQuizQuestions.filter(q => q.question_id !== questionId);
        const quiz = this.quizzes.find(q => q.quiz_id === this.selectedQuiz);
        if (quiz) quiz.questions = quiz.questions.filter(q => q.question_id !== questionId);
        this.alert = { visible: true, message: 'Question deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to delete question', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async deleteQuiz(quizId) {
      if (!confirm('Are you sure you want to delete this quiz?')) return;
      try {
        this.isSubmitting = true;
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${quizId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.quizzes = this.quizzes.filter(q => q.quiz_id !== quizId);
        this.alert = { visible: true, message: 'Quiz deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to delete quiz', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async toggleQuizVisibility(quiz) {
      try {
        this.isSubmitting = true;
        const newVisibility = !quiz.is_visible;
        await axios.put(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${this.selectedTopic}/quizzes/${quiz.quiz_id}/visibility`,
          { is_visible: newVisibility },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        quiz.is_visible = newVisibility;
        this.alert = { visible: true, message: `Quiz ${newVisibility ? 'shown' : 'hidden'} successfully`, type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: err.response?.data?.error || 'Failed to toggle visibility', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    closeViewQuestionsModal() {
      this.viewQuestionsModalVisible = false;
      this.selectedQuiz = null;
      this.selectedQuizTitle = '';
      this.selectedQuizQuestions = [];
      this.currentQuestionPage = 1;
    },
    closeGenerateQuizModal() {
      this.generateQuizModalVisible = false;
      this.newQuiz = {

        quiz_title: '',
        duration_minutes: 30
      };
      this.v$.newQuiz.$reset();
    },
    closeCreateModal() {
      this.createModalVisible = false;
      this.editingQuestion = false;
      this.newQuestion = {
        question_id: null,
        quiz_id: null,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: '',
        score_points: 1
      };
      this.v$.newQuestion.$reset();
    }
  },
  watch: {
    selectedLesson() {
      this.selectedModule = '';
      this.topics = [];
      this.selectedTopic = '';
      this.quizzes = [];
    },
    selectedModule() {
      this.topics = [];
      this.selectedTopic = '';
      this.quizzes = [];
    },
    selectedTopic() {
      this.quizzes = [];
    }
  },
  mounted() {
    this.fetchLessons();
  }
};
</script>

<style scoped>
h2, label {
  color: #000000;
}

button.btn {
  transition: all 0.2s ease;
}

button.btn:hover {
  filter: brightness(1.15);
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

button.btn:active {
  transform: translateY(0);
}

input:disabled, select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.table th, .table td {
  vertical-align: middle;
}

.table tbody tr:hover {
  background-color: #f1f3f5;
  transition: background-color 0.2s ease;
}

.table-responsive {
  overflow-x: auto;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-dialog {
  max-width: 90vw;
}

.modal-content {
  border-radius: 0.5rem;
}

.modal-body {
  max-height: 70vh;
  overflow-y: auto;
}

.btn-close:hover {
  background-color: #e9ecef;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  display: block;
  color: #dc3545;
  font-size: 0.875em;
}

@media (max-width: 576px) {
  .container {
    padding-left: 12px;
    padding-right: 12px;
  }
  h2 {
    font-size: 1.5rem;
  }
  .modal-dialog {
    margin: 1rem;
    max-width: 95vw;
  }
  .modal-body {
    padding: 1rem;
  }
  .table {
    font-size: 0.85rem;
  }
  .table th, .table td {
    padding: 0.5rem;
    white-space: nowrap;
  }
  .table-responsive {
    margin-bottom: 1rem;
  }
}
</style>
