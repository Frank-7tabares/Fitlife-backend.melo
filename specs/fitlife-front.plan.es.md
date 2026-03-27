# Plan Técnico Frontend FitLife - Proyecto Final Universitario
**Angular 21 | TypeScript | Material Design**

**Versión:** 3.0 (Frontend)  
**Fecha:** 2026-02-13  
**Contexto:** Trabajo Final Universitario

---

## 1. RESUMEN ARQUITECTÓNICO

### 1.1 Visión General

Frontend de FitLife implementado con Angular 21 (standalone components), siguiendo arquitectura modular con separación clara entre core, shared y features. El sistema consume la API REST del backend y proporciona una interfaz moderna y responsiva.

### 1.2 Stack Tecnológico

- **Framework:** Angular 21 (standalone)
- **Lenguaje:** TypeScript 5.0+
- **UI Library:** Angular Material 21
- **HTTP:** Angular HttpClient con interceptors
- **Routing:** Angular Router
- **Forms:** Reactive Forms
- **State Management:** Services con RxJS
- **Testing:** Jest + Testing Library
- **Build:** Angular CLI 21
- **Styles:** SCSS + Material Theming

### 1.3 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    APP COMPONENT                         │
│                   (Shell/Layout)                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼──────────┐
│  CORE LAYER    │      │   SHARED LAYER    │
│  (Singleton)   │      │  (Reutilizable)   │
│                │      │                   │
│ - Auth Service │      │ - Header          │
│ - API Service  │      │ - Footer          │
│ - Guards       │      │ - Pipes           │
│ - Interceptors │      │ - Directives      │
└────────────────┘      └───────────────────┘
                     │
        ┌────────────┴────────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼────────┐
│ FEATURE MODULES│              │ FEATURE MODULES  │
│                │              │                  │
│ - Auth         │              │ - Training       │
│ - Dashboard    │              │ - Nutrition      │
│ - Assessment   │              │ - Profile        │
│ - Instructors  │              │ - Messages       │
└────────────────┘              └──────────────────┘
```

### 1.4 Decisiones Arquitectónicas Clave

| Decisión | Justificación | Riesgo/Mitigación |
|----------|---------------|-------------------|
| Angular 21 Standalone | - Arquitectura moderna<br>- Menor boilerplate<br>- Mejor performance | Riesgo: Paradigma nuevo<br>Mitigación: Documentación angular.dev |
| Material Design | - Componentes probados<br>- Accesibilidad integrada<br>- Theming consistente | Riesgo: Tamaño del bundle<br>Mitigación: Importación selectiva |
| Reactive Forms | - Validación robusta<br>- Testeable<br>- Tipado fuerte | Riesgo: Curva de aprendizaje<br>Mitigación: Ejemplos claros |
| RxJS para Estado | - Observable patterns<br>- No necesita NgRx para MVP | Riesgo: Complejidad en operadores<br>Mitigación: Operadores básicos |
| Jest sobre Jasmine | - Más rápido<br>- Mejor DX<br>- Snapshot testing | Riesgo: Compatibilidad<br>Mitigación: @angular-builders |

---

## 2. ESTRUCTURA DEL PROYECTO

```
fitlife-frontend/
├── src/
│   ├── app/
│   │   ├── core/                       # Servicios singleton
│   │   │   ├── auth/
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── auth.guard.ts
│   │   │   │   ├── token.interceptor.ts
│   │   │   │   └── auth.models.ts
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts
│   │   │   │   ├── error-handler.service.ts
│   │   │   │   └── storage.service.ts
│   │   │   └── interceptors/
│   │   │       ├── http-error.interceptor.ts
│   │   │       └── loading.interceptor.ts
│   │   │
│   │   ├── shared/                     # Componentes compartidos
│   │   │   ├── components/
│   │   │   │   ├── header/
│   │   │   │   ├── footer/
│   │   │   │   ├── loading-spinner/
│   │   │   │   └── error-message/
│   │   │   ├── pipes/
│   │   │   │   ├── bmi.pipe.ts
│   │   │   │   └── fitness-category.pipe.ts
│   │   │   └── directives/
│   │   │       └── autofocus.directive.ts
│   │   │
│   │   ├── features/                   # Módulos de funcionalidad
│   │   │   ├── auth/
│   │   │   │   ├── components/
│   │   │   │   │   ├── login/
│   │   │   │   │   ├── register/
│   │   │   │   │   ├── reset-password/
│   │   │   │   │   └── change-password/
│   │   │   │   ├── auth.routes.ts
│   │   │   │   └── auth.service.ts
│   │   │   ├── dashboard/
│   │   │   ├── assessment/
│   │   │   ├── instructors/
│   │   │   ├── training/
│   │   │   ├── nutrition/
│   │   │   ├── profile/
│   │   │   └── messages/
│   │   │
│   │   ├── app.routes.ts
│   │   ├── app.config.ts
│   │   └── app.component.ts
│   │
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.development.ts
│   ├── styles/
│   │   ├── _variables.scss
│   │   ├── _material-theme.scss
│   │   └── styles.scss
│   ├── index.html
│   └── main.ts
│
├── tests/
├── angular.json
├── jest.config.js
├── package.json
├── tsconfig.json
└── README.md
```

---

## 3. FASES DEL PROYECTO

### FASE 0: Configuración del Entorno

#### Objetivo
Preparar el entorno de desarrollo frontend con Angular 21 y todas las herramientas necesarias.

#### Entregables

1. **Proyecto Angular:**
   - Proyecto Angular 21 inicializado
   - Angular Material 21 configurado
   - Estructura de carpetas (core, shared, features)

2. **Herramientas de Testing:**
   - Jest configurado
   - ESLint configurado
   - Prettier configurado

3. **Configuración de Estilos:**
   - Material theme personalizado
   - Variables globales SCSS
   - Responsive breakpoints

#### Actividades Detalladas

**1. Inicializar Angular 21:**

```bash
# Instalar Angular CLI 21
npm install -g @angular/cli@21

# Crear proyecto (standalone por defecto)
ng new fitlife-frontend --routing --style=scss --standalone

cd fitlife-frontend

# Instalar Angular Material 21
ng add @angular/material

# Instalar Jest
ng add @angular-builders/jest

# Instalar ESLint
ng add @angular-eslint/schematics
```

**2. Configurar `package.json`:**

```json
{
  "name": "fitlife-frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "ng serve",
    "build": "ng build",
    "test": "ng test",
    "test:coverage": "ng test --code-coverage",
    "lint": "ng lint"
  },
  "dependencies": {
    "@angular/animations": "^21.0.0",
    "@angular/common": "^21.0.0",
    "@angular/compiler": "^21.0.0",
    "@angular/core": "^21.0.0",
    "@angular/forms": "^21.0.0",
    "@angular/material": "^21.0.0",
    "@angular/platform-browser": "^21.0.0",
    "@angular/router": "^21.0.0",
    "rxjs": "^7.8.0",
    "tslib": "^2.3.0"
  },
  "devDependencies": {
    "@angular-builders/jest": "^21.0.0",
    "@angular-devkit/build-angular": "^21.0.0",
    "@angular-eslint/schematics": "^21.0.0",
    "@angular/cli": "^21.0.0",
    "@angular/compiler-cli": "^21.0.0",
    "@testing-library/angular": "^15.0.0",
    "jest": "^29.0.0",
    "typescript": "~5.0.0"
  }
}
```

**3. Configurar Jest (`jest.config.js`):**

```javascript
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['html', 'text', 'lcov'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**4. Configurar ESLint (`.eslintrc.json`):**

```json
{
  "root": true,
  "overrides": [
    {
      "files": ["*.ts"],
      "extends": [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:@angular-eslint/recommended"
      ],
      "rules": {
        "@angular-eslint/component-selector": [
          "error",
          {
            "prefix": "app",
            "style": "kebab-case",
            "type": "element"
          }
        ]
      }
    }
  ]
}
```

**5. Configurar Material Theme:**

```scss
// src/styles/_material-theme.scss
@use '@angular/material' as mat;

$fitlife-primary: mat.define-palette(mat.$indigo-palette);
$fitlife-accent: mat.define-palette(mat.$pink-palette, A200, A100, A400);
$fitlife-warn: mat.define-palette(mat.$red-palette);

$fitlife-theme: mat.define-light-theme((
  color: (
    primary: $fitlife-primary,
    accent: $fitlife-accent,
    warn: $fitlife-warn,
  )
));

@include mat.all-component-themes($fitlife-theme);
```

**6. Crear Variables Globales:**

```scss
// src/styles/_variables.scss
$primary-color: #3f51b5;
$accent-color: #ff4081;
$success-color: #4caf50;

$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;

$breakpoint-mobile: 600px;
$breakpoint-tablet: 960px;
$breakpoint-desktop: 1280px;
```

**7. Configurar Environments:**

```typescript
// src/environments/environment.development.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};

// src/environments/environment.ts
export const environment = {
  production: true,
  apiUrl: 'http://localhost:8000'
};
```

#### Criterios de Aceptación
- [ ] Proyecto Angular 21 creado
- [ ] Angular Material configurado
- [ ] Frontend responde en `http://localhost:4200`
- [ ] `ng test` ejecuta con Jest
- [ ] ESLint pasa sin errores
- [ ] Estructura de carpetas creada

---

### FASE 1: Core Layer (Servicios Fundamentales)

#### Objetivo
Implementar servicios singleton del core: autenticación, API, storage, guards e interceptors.

#### Entregables

1. **AuthService:**
   - Login/logout
   - Gestión de estado de usuario
   - Tokens JWT

2. **ApiService:**
   - Cliente HTTP base
   - Configuración de URLs

3. **StorageService:**
   - Wrapper de localStorage
   - Gestión de tokens

4. **Guards:**
   - AuthGuard
   - RoleGuard

5. **Interceptors:**
   - TokenInterceptor
   - HttpErrorInterceptor
   - LoadingInterceptor

#### Ejemplo de Implementación

**AuthService:**

```typescript
// src/app/core/auth/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthResponse {
  user_id: string;
  email: string;
  role: string;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  private apiUrl = `${environment.apiUrl}/api/auth`;

  constructor(
    private http: HttpClient,
    private storage: StorageService
  ) {
    this.loadUserFromStorage();
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, { email, password })
      .pipe(
        tap(response => {
          this.storage.setAccessToken(response.access_token);
          this.storage.setRefreshToken(response.refresh_token);
          this.currentUserSubject.next({
            id: response.user_id,
            email: response.email,
            role: response.role
          });
        })
      );
  }

  logout(): void {
    this.storage.clearTokens();
    this.currentUserSubject.next(null);
  }

  isAuthenticated(): boolean {
    return !!this.storage.getAccessToken();
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  private loadUserFromStorage(): void {
    const token = this.storage.getAccessToken();
    if (token) {
      // Decode JWT y cargar usuario
      // (implementar decodificación)
    }
  }
}
```

**AuthGuard:**

```typescript
// src/app/core/auth/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isAuthenticated()) {
    return true;
  }
  
  router.navigate(['/auth/login'], { 
    queryParams: { returnUrl: state.url }
  });
  return false;
};
```

**TokenInterceptor:**

```typescript
// src/app/core/auth/token.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { StorageService } from '../services/storage.service';

export const tokenInterceptor: HttpInterceptorFn = (req, next) => {
  const storage = inject(StorageService);
  const token = storage.getAccessToken();
  
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
  
  return next(req);
};
```

#### Tests Unitarios

```typescript
// src/app/core/auth/auth.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should login successfully', () => {
    const mockResponse = {
      user_id: '123',
      email: 'test@example.com',
      role: 'USER',
      access_token: 'token123',
      refresh_token: 'refresh123',
      expires_in: 1800
    };
    
    service.login('test@example.com', 'password').subscribe(response => {
      expect(response).toEqual(mockResponse);
    });
    
    const req = httpMock.expectOne('http://localhost:8000/api/auth/login');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });
});
```

#### Criterios de Aceptación
- [ ] AuthService implementado con login/logout
- [ ] Guards protegen rutas correctamente
- [ ] Interceptors añaden token a solicitudes
- [ ] **Cobertura >= 85% en core**
- [ ] Tests unitarios pasan

---

### FASE 2: Shared Layer (Componentes Reutilizables)

#### Objetivo
Implementar componentes, pipes y directives compartidos en toda la aplicación.

#### Entregables

1. **Componentes Compartidos:**
   - HeaderComponent
   - FooterComponent
   - LoadingSpinnerComponent
   - ErrorMessageComponent
   - ConfirmationDialogComponent

2. **Pipes:**
   - BMIPipe
   - FitnessCategoryPipe
   - DateFormatPipe

3. **Directives:**
   - AutofocusDirective
   - HighlightDirective

#### Ejemplo de Implementación

**HeaderComponent:**

```typescript
// src/app/shared/components/header/header.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatBadgeModule } from '@angular/material/badge';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatBadgeModule
  ],
  template: `
    <mat-toolbar color="primary">
      <span>FitLife</span>
      <span class="spacer"></span>
      
      @if (authService.currentUser$ | async; as user) {
        <button mat-button [routerLink]="['/dashboard']">Dashboard</button>
        <button mat-button [routerLink]="['/assessment']">Evaluación</button>
        <button mat-button [routerLink]="['/training']">Entrenamiento</button>
        <button mat-icon-button [routerLink]="['/messages']">
          <mat-icon [matBadge]="3" matBadgeColor="warn">notifications</mat-icon>
        </button>
        <button mat-button (click)="logout()">Salir</button>
      }
    </mat-toolbar>
  `,
  styles: [`
    .spacer {
      flex: 1 1 auto;
    }
  `]
})
export class HeaderComponent {
  constructor(public authService: AuthService) {}
  
  logout(): void {
    this.authService.logout();
  }
}
```

**BMIPipe:**

```typescript
// src/app/shared/pipes/bmi.pipe.ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'bmi',
  standalone: true
})
export class BMIPipe implements PipeTransform {
  transform(weight: number, height: number): string {
    if (!weight || !height) return '-';
    const bmi = weight / Math.pow(height / 100, 2);
    return bmi.toFixed(1);
  }
}
```

#### Criterios de Aceptación
- [ ] Componentes compartidos implementados
- [ ] Pipes funcionan correctamente
- [ ] Directives se aplican correctamente
- [ ] **Cobertura >= 80% en shared**
- [ ] Componentes son reutilizables

---

### FASE 3: Feature Modules - Autenticación y Dashboard

#### Objetivo
Implementar módulos de autenticación (login, register, reset password) y dashboard.

#### Entregables

1. **Auth Feature:**
   - LoginComponent
   - RegisterComponent
   - ResetPasswordComponent
   - ChangePasswordComponent

2. **Dashboard Feature:**
   - DashboardHomeComponent
   - StatsCardComponent
   - QuickActionsComponent

#### Ejemplo de Implementación

**LoginComponent:**

```typescript
// src/app/features/auth/components/login/login.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>Iniciar Sesión</mat-card-title>
      </mat-card-header>
      
      <mat-card-content>
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="outline">
            <mat-label>Email</mat-label>
            <input matInput formControlName="email" type="email">
            @if (loginForm.get('email')?.hasError('email')) {
              <mat-error>Email inválido</mat-error>
            }
          </mat-form-field>
          
          <mat-form-field appearance="outline">
            <mat-label>Contraseña</mat-label>
            <input matInput formControlName="password" type="password">
            @if (loginForm.get('password')?.hasError('required')) {
              <mat-error>Contraseña requerida</mat-error>
            }
          </mat-form-field>
          
          <button mat-raised-button color="primary" type="submit" 
                  [disabled]="loginForm.invalid">
            Iniciar Sesión
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `
})
export class LoginComponent {
  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}
  
  onSubmit(): void {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login(email!, password!).subscribe({
        next: () => this.router.navigate(['/dashboard']),
        error: (error) => console.error('Login failed', error)
      });
    }
  }
}
```

#### Criterios de Aceptación
- [ ] LoginComponent funciona correctamente
- [ ] RegisterComponent valida formularios
- [ ] ResetPasswordComponent envía solicitud
- [ ] Dashboard muestra resumen de usuario
- [ ] **Cobertura >= 80%**

---

### FASE 4: Feature Modules - Assessment e Instructors

#### Objetivo
Implementar módulos de evaluación física y gestión de instructores.

#### Entregables

1. **Assessment Feature:**
   - AssessmentFormComponent
   - AssessmentResultsComponent
   - AssessmentHistoryComponent

2. **Instructors Feature:**
   - InstructorListComponent
   - InstructorCardComponent
   - InstructorDetailComponent
   - InstructorRatingComponent

#### Ejemplo de Implementación

**AssessmentService:**

```typescript
// src/app/features/assessment/services/assessment.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

interface AssessmentResponse {
  id: string;
  fitness_score: number;
  fitness_category: string;
  body_age: number;
  real_age: number;
  age_difference: number;
}

@Injectable({ providedIn: 'root' })
export class AssessmentService {
  private apiUrl = `${environment.apiUrl}/api/assessments`;

  constructor(private http: HttpClient) {}

  submitAssessment(responses: any): Observable<AssessmentResponse> {
    return this.http.post<AssessmentResponse>(this.apiUrl, responses);
  }

  getAssessmentHistory(userId: string): Observable<AssessmentResponse[]> {
    return this.http.get<AssessmentResponse[]>(`${environment.apiUrl}/api/users/${userId}/assessments`);
  }
}
```

#### Criterios de Aceptación
- [ ] Formulario de evaluación funciona
- [ ] Resultados se muestran correctamente
- [ ] Lista de instructores se carga
- [ ] Asignación de instructor funciona
- [ ] **Cobertura >= 80%**

---

### FASE 5: Feature Modules - Training, Nutrition y Profile

#### Objetivo
Implementar módulos de entrenamiento, nutrición y perfil de usuario.

#### Entregables

1. **Training Feature:**
   - ActiveRoutineComponent
   - ExerciseListComponent
   - WorkoutCompletionComponent
   - WorkoutHistoryComponent

2. **Nutrition Feature:**
   - NutritionPlanComponent
   - DailyMealsComponent
   - MealCardComponent

3. **Profile Feature:**
   - ProfileViewComponent
   - ProfileEditComponent
   - PhysicalRecordsComponent
   - ProgressChartsComponent

#### Ejemplo de Implementación

**TrainingService:**

```typescript
// src/app/features/training/services/training.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

interface Routine {
  id: string;
  goal_description: string;
  fitness_level: string;
  exercises: Exercise[];
}

interface Exercise {
  name: string;
  sets: number;
  reps: number;
  rest_seconds: number;
}

@Injectable({ providedIn: 'root' })
export class TrainingService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  getActiveRoutine(userId: string): Observable<Routine> {
    return this.http.get<Routine>(`${this.apiUrl}/users/${userId}/routines/active`);
  }

  completeWorkout(workoutId: string, completion: any): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/workouts/${workoutId}/complete`, completion);
  }
}
```

#### Criterios de Aceptación
- [ ] Rutina activa se muestra correctamente
- [ ] Completación de entrenamientos funciona
- [ ] Plan de nutrición se visualiza
- [ ] Edición de perfil funciona
- [ ] **Cobertura >= 80%**

---

### FASE 6: Integración, Testing y Refinamiento

#### Objetivo
Asegurar integración completa, cobertura >= 80%, y refinamiento de UI/UX.

#### Actividades

1. **Tests de Integración:**
   - Flujos completos de usuario
   - Integración con API backend

2. **Verificación de Cobertura:**
   - Ejecutar `ng test --code-coverage`
   - Verificar >= 80% global

3. **Refinamiento UI/UX:**
   - Diseño responsivo verificado
   - Accesibilidad básica
   - Loading states
   - Mensajes de error amigables

4. **Performance:**
   - Lazy loading verificado
   - Bundle size optimizado

#### Ejemplo de Test de Integración

```typescript
// tests/integration/login.spec.ts
import { render, screen, fireEvent, waitFor } from '@testing-library/angular';
import { LoginComponent } from '../../src/app/features/auth/components/login/login.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('Login Integration', () => {
  it('should login successfully', async () => {
    await render(LoginComponent, {
      imports: [HttpClientTestingModule]
    });
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Contraseña');
    const submitButton = screen.getByRole('button', { name: 'Iniciar Sesión' });
    
    fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.input(passwordInput, { target: { value: 'SecurePass123!' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });
});
```

#### Criterios de Aceptación
- [ ] Cobertura >= 80%
- [ ] Todos los tests de integración pasan
- [ ] Diseño responsivo funciona
- [ ] Performance aceptable
- [ ] No hay errores de lint
- [ ] Documentación completa

---

## 4. ESTRATEGIA DE PRUEBAS

### 4.1 Cobertura Mínima: 80% Global

| Tipo | Herramienta | Cobertura Objetivo |
|------|-------------|-------------------|
| Unitarias | Jest | >= 80% |
| Integración | Testing Library | >= 75% |
| Componentes | Jest + Testing Library | >= 80% |
| Servicios | Jest | >= 85% |

### 4.2 Ejecución de Tests

```bash
# Ejecutar todos los tests
ng test

# Ejecutar con cobertura
ng test --code-coverage

# Ejecutar en modo watch
ng test --watch
```

---

## 5. NOTIFICACIONES BÁSICAS

### 5.1 Funcionalidad Básica

- **Badge de notificaciones:** Contador de mensajes no leídos
- **Mensajes en la aplicación:** Consulta manual

### 5.2 Implementación

```typescript
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private unreadCountSubject = new BehaviorSubject<number>(0);
  public unreadCount$ = this.unreadCountSubject.asObservable();
  
  loadUnreadCount(userId: string): void {
    this.messageService.getMessages(userId).subscribe(messages => {
      const unread = messages.filter(m => !m.is_read).length;
      this.unreadCountSubject.next(unread);
    });
  }
}
```

---

## 6. SEGURIDAD

### 6.1 Almacenamiento de Tokens
- Tokens en localStorage
- Limpieza al cerrar sesión

### 6.2 Validación de Formularios
- Formato de email
- Complejidad de contraseña
- Campos requeridos

### 6.3 Protección XSS
- Sanitización automática de Angular
- Uso de DomSanitizer

---

## 7. CRITERIOS DE ACEPTACIÓN

### 7.1 Funcionalidad
- [ ] Todas las historias de usuario implementadas
- [ ] Navegación funciona
- [ ] Formularios validan
- [ ] Autenticación funciona

### 7.2 Calidad
- [ ] Cobertura >= 80%
- [ ] ESLint pasa
- [ ] Arquitectura respetada

### 7.3 UI/UX
- [ ] Diseño responsivo
- [ ] Material theme aplicado
- [ ] Loading states
- [ ] Mensajes de error

---

## 8. RUTAS DE LA APLICACIÓN

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard-home/dashboard-home.component'),
    canActivate: [authGuard]
  },
  {
    path: 'assessment',
    loadChildren: () => import('./features/assessment/assessment.routes'),
    canActivate: [authGuard]
  },
  // ... demás rutas
];
```

---

## FIN DEL PLAN TÉCNICO FRONTEND

Este plan está estructurado por fases de implementación, desde la configuración inicial hasta la integración y testing, con cobertura mínima de 80%, notificaciones básicas y arquitectura modular con Angular 21 standalone.
