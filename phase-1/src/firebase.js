import { initializeApp } from 'firebase/app'
import { 
  getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged 
} from 'firebase/auth'
import { 
  getFirestore, collection, query, orderBy, limit, onSnapshot, addDoc, serverTimestamp 
} from 'firebase/firestore'
import { ref, onUnmounted, computed, watchEffect } from 'vue'

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB5QgbeoTiJ5HlFlhxq_7OSkE26CNFyRss",
  authDomain: "team-git-lucky.firebaseapp.com",
  projectId: "team-git-lucky",
  storageBucket: "team-git-lucky.firebasestorage.app",
  messagingSenderId: "68085181113",
  appId: "1:68085181113:web:9449a467fde40707f44968",
  measurementId: "G-6XEJS8LMVV"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const firestore = getFirestore(app)

// Authentication Hook
export function useAuth() {
  const user = ref(null)
  const isLogin = computed(() => user.value !== null)

  const unsubscribe = onAuthStateChanged(auth, (_user) => {
    user.value = _user
  })

  onUnmounted(unsubscribe)

  const signIn = async () => {
    const googleProvider = new GoogleAuthProvider()
    await signInWithPopup(auth, googleProvider)
  }

  const signOutUser = async () => {
    await signOut(auth)
    user.value = null // Ensure user state is cleared
  }

  return { user, isLogin, signIn, signOut: signOutUser }
}

// Chat Hook
export function useChat() {
  const messages = ref([])
  let unsubscribe = null

  const { user, isLogin } = useAuth()

  // Fetch messages only when the user is logged in
  watchEffect(() => {
    if (isLogin.value) {
      const messagesCollection = collection(firestore, 'messages')
      const messagesQuery = query(messagesCollection, orderBy('createdAt', 'desc'), limit(100))

      unsubscribe = onSnapshot(messagesQuery, (snapshot) => {
        messages.value = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })).reverse()
      })
    } else {
      messages.value = [] // Clear messages when user logs out
      if (unsubscribe) unsubscribe() // Stop listening to Firestore
    }
  })

  const sendMessage = async (text) => {
    if (!isLogin.value) return
    const { photoURL, uid, displayName } = user.value

    await addDoc(collection(firestore, 'messages'), {
      userName: displayName,
      userId: uid,
      userPhotoURL: photoURL,
      text: text,
      createdAt: serverTimestamp()
    })
  }

  return { messages, sendMessage }
}
