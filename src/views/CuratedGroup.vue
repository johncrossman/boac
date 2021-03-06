<template>
  <div class="m-3">
    <Spinner alert-prefix="Curated group" />
    <div v-if="!loading">
      <CuratedGroupHeader />
      <div v-show="mode !== 'bulkAdd'">
        <hr v-if="!error && totalStudentCount" class="filters-section-separator" />
        <div class="cohort-column-results">
          <div v-if="totalStudentCount > 1" class="d-flex m-2">
            <div class="cohort-list-header-column-01"></div>
            <div class="cohort-list-header-column-02">
              <SortBy v-if="totalStudentCount > 1" />
            </div>
          </div>
          <div v-if="size(students)">
            <div id="curated-cohort-students" class="list-group">
              <StudentRow
                v-for="(student, index) in students"
                :id="`student-${student.uid}`"
                :key="student.sid"
                :remove-student="removeStudent"
                :row-index="index"
                :student="student"
                :list-type="ownerId === $currentUser.id ? 'curatedGroupForOwner' : 'curatedGroup'"
                :sorted-by="preferences.sortBy"
                :class="{'list-group-item-info': anchor === `#${student.uid}`}"
                class="list-group-item student-list-item" />
            </div>
            <div v-if="totalStudentCount > itemsPerPage" class="p-3">
              <Pagination
                :click-handler="onClickPagination"
                :init-page-number="pageNumber"
                :limit="10"
                :per-page="itemsPerPage"
                :total-rows="totalStudentCount" />
            </div>
          </div>
        </div>
      </div>
      <div v-if="!loading && mode === 'bulkAdd'">
        <h2 class="page-section-header-sub">Add Students</h2>
        <div class="w-75">
          Type or paste a list of Student Identification (SID) numbers below. Example: 9999999990, 9999999991
        </div>
        <CuratedGroupBulkAdd :bulk-add-sids="bulkAddSids" :curated-group-id="curatedGroupId" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Loading from '@/mixins/Loading'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import StudentRow from '@/components/student/StudentRow'
import Util from '@/mixins/Util'

export default {
  name: 'CuratedGroup',
  components: {
    CuratedGroupBulkAdd,
    CuratedGroupHeader,
    Pagination,
    SortBy,
    Spinner,
    StudentRow
  },
  mixins: [Context, CuratedEditSession, CurrentUserExtras, Loading, Scrollable, Util],
  props: {
    id: {
      required: true,
      type: [String, Number]
    }
  },
  data: () => ({
    error: undefined
  }),
  computed: {
    anchor: () => location.hash
  },
  created() {
    this.$eventHub.$off('sortBy-user-preference-change')
    this.setMode(undefined)
    this.init(parseInt(this.id)).then(group => {
      if (group) {
        this.loaded(group.name)
        this.setPageTitle(this.curatedGroupName)
        this.putFocusNextTick('curated-group-name')
        if (this.pageNumber > 1) {
          this.alertScreenReader(`Go to page ${this.pageNumber}`)
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, this.screenReaderAlert)
        }
      } else {
        this.$router.push({ path: '/404' })
      }
    })
    this.$eventHub.$on('sortBy-user-preference-change', sortBy => {
      if (!this.loading) {
        this.loadingStart()
        this.goToPage(1).then(() => {
          this.loaded(this.curatedGroupName)
          this.alertScreenReader(`Students sorted by ${sortBy}`)
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, this.screenReaderAlert)
        })
      }
    })
  },
  mounted() {
    this.$nextTick(function() {
      if (!this.anchor) {
        return false
      }
      let anchor = this.anchor.replace(/(#)([0-9])/g, function(a, m1, m2) {
        return `${m1}student-${m2}`
      })
      this.scrollTo(anchor)
    })
  },
  methods: {
    bulkAddSids(sids) {
      this.setMode(undefined)
      if (this.size(sids)) {
        this.alertScreenReader(`Adding ${sids.length} students`)
        store.commit('currentUserExtras/setUserPreference', {
          key: 'sortBy',
          value: 'last_name'
        })
        this.loadingStart()
        this.addStudents(sids).then(() => {
          this.loaded(this.name)
          this.putFocusNextTick('curated-group-name')
          this.alertScreenReader(`${sids.length} students added to group '${this.name}'`)
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, 'Update curated group with bulk-add SIDs')
        })
      } else {
        this.alertScreenReader('Cancelled bulk add of students')
        this.putFocusNextTick('curated-group-name')
      }
    },
    onClickPagination(pageNumber) {
      this.loadingStart()
      this.goToPage(pageNumber).then(() => {
        this.loaded(this.name)
        this.alertScreenReader(`Page ${pageNumber} of cohort ${this.curatedGroupName}`)
        this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName,this.screenReaderAlert)
      })
    }
  }
}
</script>

<style scoped>
h3 {
  color: #666;
  font-size: 18px;
}
.cohort-list-header-column-01 {
  flex: 0 0 52px;
}
.cohort-list-header-column-02 {
  margin-left: auto;
  white-space: nowrap;
}
.student-list-item {
  border-left: none;
  border-right: none;
  display: flex;
}
</style>
