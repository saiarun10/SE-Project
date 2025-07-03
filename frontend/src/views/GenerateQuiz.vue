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
      <div class="text-center mb-4">
        <button class="btn btn-primary" @click="fetchTopics" :disabled="!selectedLesson || !selectedModule || isSubmitting">
          Submit
        </button>
      </div>
      <div v-if="topics.length" class="table-responsive">
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Topic</th>
              <th>Quizzes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="topic in topics" :key="topic.topic_id">
              <td>{{ topic.topic_title }}</td>
              <td>
                <div v-if="topic.quizzes && topic.quizzes.length" class="mb-2">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>Quiz Title</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(quiz, index) in paginatedQuizzes(topic.quizzes)" :key="quiz.quiz_id">
                        <td>{{ quiz.quiz_title }}</td>
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
                      <li class="page-item" :class="{ 'disabled': topic.currentQuizPage === 1 }">
                        <button class="page-link" @click="changeQuizPage(topic.topic_id, -1)">Previous</button>
                      </li>
                      <li class="page-item" v-for="page in quizPageCount(topic.quizzes)" :key="page" :class="{ 'active': topic.currentQuizPage === page }">
                        <button class="page-link" @click="changeQuizPage(topic.topic_id, page)">{{ page }}</button>
                      </li>
                      <li class="page-item" :class="{ 'disabled': topic.currentQuizPage === quizPageCount(topic.quizzes) }">
                        <button class="page-link" @click="changeQuizPage(topic.topic_id, 1)">Next</button>
                      </li>
                    </ul>
                  </nav>
                </div>
                <div v-else>
                  <p>No quizzes available. <button class="btn btn-success btn-sm" @click="generateQuizModal(topic.topic_id)" :disabled="isSubmitting">Generate Quiz</button></p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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
              <p>No questions available. <button class="btn btn-primary btn-sm" @click="createQuestionModal">Create First Question</button></p>
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
                    <button class="page-link" @click="changeQuestionPage(-1)">Previous</button>
                  </li>
                  <li class="page-item" v-for="page in questionPageCount" :key="page" :class="{ 'active': currentQuestionPage === page }">
                    <button class="page-link" @click="changeQuestionPage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ 'disabled': currentQuestionPage === questionPageCount }">
                    <button class="page-link" @click="changeQuestionPage(1)">Next</button>
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
                  <option v-for="option in ['option1', 'option2', 'option3', 'option4']" :key="option" :value="option">
                    {{ newQuestion[option] || option }}
                  </option>
                  <div v-for="error in v$.newQuestion.correct_answer.$errors" :key="error.$uid" class="invalid-feedback">{{ error.$message }}</div>
                </select>
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting || v$.$invalid">
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
import { required } from '@vuelidate/validators';

export default {
  name: 'GenerateQuiz',
  components: { Alert, Navbar, AppFooter },
  setup() {
    return { v$: useVuelidate() };
  },
  data() {
    return {
      lessons: [],
      modules: [],
      topics: [],
      selectedLesson: '',
      selectedModule: '',
      selectedQuiz: null,
      selectedQuizTitle: '',
      selectedQuizQuestions: [],
      viewQuestionsModalVisible: false,
      createModalVisible: false,
      editingQuestion: false,
      newQuestion: {
        question_id: null,
        quiz_id: null,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: ''
      },
      isSubmitting: false,
      alert: { visible: false, message: '', type: 'notification' },
      itemsPerPage: 5,
      currentQuestionPage: 1
    };
  },
  validations() {
    return {
      newQuestion: {
        question_text: { required },
        option1: { required },
        option2: { required },
        option3: { required },
        option4: { required },
        correct_answer: { required }
      }
    };
  },
  computed: {
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
    paginatedQuizzes(quizzes) {
      const start = (this.getCurrentQuizPage(quizzes) - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return quizzes.slice(start, end);
    },
    quizPageCount(quizzes) {
      return Math.ceil(quizzes.length / this.itemsPerPage);
    },
    getCurrentQuizPage(quizzes) {
      const topic = this.topics.find(t => t.quizzes === quizzes);
      return topic ? topic.currentQuizPage || 1 : 1;
    },
    changeQuizPage(topicId, page) {
      const topic = this.topics.find(t => t.topic_id === topicId);
      if (!topic) return;
      if (typeof page === 'number') {
        topic.currentQuizPage = page;
      } else {
        topic.currentQuizPage = Math.max(1, Math.min(this.quizPageCount(topic.quizzes), topic.currentQuizPage + page));
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
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/get_all_lessons`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.lessons = response.data;
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load lessons', type: 'error' };
      }
    },
    async fetchModules() {
      if (!this.selectedLesson) {
        this.modules = [];
        this.selectedModule = '';
        this.topics = [];
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/modules`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.modules = response.data;
        this.selectedModule = '';
        this.topics = [];
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load modules', type: 'error' };
      }
    },
    async fetchTopics() {
      if (!this.selectedLesson || !this.selectedModule) {
        this.topics = [];
        return;
      }
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topics`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        this.topics = response.data.map(topic => ({
          ...topic,
          quizzes: topic.quizzes || [],
          currentQuizPage: 1
        }));
        for (const topic of this.topics) {
          await this.fetchQuizzesForTopic(topic.topic_id);
        }
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to load topics', type: 'error' };
      }
    },
    async fetchQuizzesForTopic(topicId) {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/quizzes`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        const topic = this.topics.find(t => t.topic_id === topicId);
        if (topic) {
          topic.quizzes = response.data;
          for (const quiz of topic.quizzes) {
            await this.fetchQuestionsForQuiz(quiz.quiz_id);
          }
        }
      } catch (err) {
        this.alert = { visible: true, message: `Failed to load quizzes for topic ${topicId}`, type: 'error' };
      }
    },
    async fetchQuestionsForQuiz(quizId) {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${quizId}/questions`, {
          headers: { Authorization: `Bearer ${this.$store.state.token}` }
        });
        const quiz = this.topics.flatMap(t => t.quizzes).find(q => q.quiz_id === quizId);
        if (quiz) {
          quiz.questions = response.data;
        }
      } catch (err) {
        this.alert = { visible: true, message: `Failed to load questions for quiz ${quizId}`, type: 'error' };
      }
    },
    async generateQuizModal(topicId) {
      this.selectedQuiz = null;
      this.createModalVisible = true;
      this.newQuestion = {
        question_id: null,
        quiz_id: null,
        question_text: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_answer: ''
      };
      this.editingQuestion = false;
      try {
        const payload = {
          quiz_title: `Quiz for Topic ${this.topics.find(t => t.topic_id === topicId).topic_title}`,
          duration_minutes: 30
        };
        const response = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/${topicId}/quiz/create`,
          payload,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        const newQuiz = response.data;
        const topic = this.topics.find(t => t.topic_id === topicId);
        if (topic) {
          topic.quizzes.push(newQuiz);
          this.newQuestion.quiz_id = newQuiz.quiz_id;
        }
        this.alert = { visible: true, message: 'Quiz created successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to create quiz', type: 'error' };
      }
    },
    createFirstQuestionModal(quizId) {
      this.selectedQuiz = quizId;
      const quiz = this.topics.flatMap(t => t.quizzes).find(q => q.quiz_id === quizId);
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
        correct_answer: ''
      };
      this.editingQuestion = false;
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
        correct_answer: ''
      };
      this.editingQuestion = false;
    },
    async saveQuestion() {
      const isValid = await this.v$.$validate();
      if (!isValid) {
        this.alert = { visible: true, message: 'Please fill all required fields', type: 'error' };
        return;
      }
      this.isSubmitting = true;
      try {
        const payload = {
          question_text: this.newQuestion.question_text,
          option1: this.newQuestion.option1,
          option2: this.newQuestion.option2,
          option3: this.newQuestion.option3,
          option4: this.newQuestion.option4,
          correct_answer: this.newQuestion.correct_answer
        };
        const endpoint = this.editingQuestion
          ? `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${this.newQuestion.quiz_id}/question/${this.newQuestion.question_id}/update`
          : `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${this.newQuestion.quiz_id}/question/create`;
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
        this.alert = { visible: true, message: this.editingQuestion ? 'Failed to update question' : 'Failed to create question', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    viewQuestions(quizId) {
      this.selectedQuiz = quizId;
      const quiz = this.topics.flatMap(t => t.quizzes).find(q => q.quiz_id === quizId);
      this.selectedQuizTitle = quiz ? quiz.quiz_title : 'Unknown Quiz';
      this.selectedQuizQuestions = quiz ? quiz.questions || [] : [];
      this.currentQuestionPage = 1;
      this.viewQuestionsModalVisible = true;
    },
    editQuestion(question) {
      this.newQuestion = { ...question };
      this.editingQuestion = true;
      this.createModalVisible = true;
    },
    async deleteQuestion(questionId) {
      if (!confirm('Are you sure you want to delete this question?')) return;
      this.isSubmitting = true;
      try {
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${this.selectedQuiz}/question/${questionId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        this.selectedQuizQuestions = this.selectedQuizQuestions.filter(q => q.question_id !== questionId);
        const quiz = this.topics.flatMap(t => t.quizzes).find(q => q.quiz_id === this.selectedQuiz);
        if (quiz) quiz.questions = quiz.questions.filter(q => q.question_id !== questionId);
        this.alert = { visible: true, message: 'Question deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to delete question', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async deleteQuiz(quizId) {
      if (!confirm('Are you sure you want to delete this quiz?')) return;
      this.isSubmitting = true;
      try {
        await axios.delete(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${quizId}/delete`,
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        for (const topic of this.topics) {
          topic.quizzes = topic.quizzes.filter(q => q.quiz_id !== quizId);
        }
        this.alert = { visible: true, message: 'Quiz deleted successfully', type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to delete quiz', type: 'error' };
      } finally {
        this.isSubmitting = false;
      }
    },
    async toggleQuizVisibility(quiz) {
      this.isSubmitting = true;
      try {
        const newVisibility = !quiz.is_visible;
        await axios.put(
          `${import.meta.env.VITE_BASE_URL}/api/${this.selectedLesson}/module/${this.selectedModule}/topic/quizzes/${quiz.quiz_id}/visibility`,
          { is_visible: newVisibility },
          { headers: { Authorization: `Bearer ${this.$store.state.token}` } }
        );
        quiz.is_visible = newVisibility;
        this.alert = { visible: true, message: `Quiz ${newVisibility ? 'shown' : 'hidden'} successfully`, type: 'success' };
      } catch (err) {
        this.alert = { visible: true, message: 'Failed to toggle visibility', type: 'error' };
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
        correct_answer: ''
      };
      this.v$.$reset();
    }
  },
  watch: {
    selectedLesson() {
      this.selectedModule = '';
      this.topics = [];
    },
    selectedModule() {
      this.topics = [];
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
  .btn-sm {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
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